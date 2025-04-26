import openai
import re
import json
import time
import random
from typing import List, Dict, Any, Optional, Tuple
from config import settings
from random_stats import generate_random_blobs
from blob_image_generator import BlobImageGenerator

openai.api_key = settings.openai_api_key

class OpenAIClient:
    """Enhanced OpenAI API client with error handling and optimized parameters"""
    
    @staticmethod
    def ask_gpt(messages: list, 
                temperature: float = 0.7, 
                top_p: float = 1.0,
                presence_penalty: float = 0.0, 
                frequency_penalty: float = 0.3,
                max_retries: int = 3,
                retry_delay: int = 2) -> str:
        """
        Enhanced version of ask_openai with better parameter control and error handling
        """
        attempt = 0
        while attempt < max_retries:
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=temperature,           # Controls randomness (0-1)
                    top_p=top_p,                       # Nucleus sampling parameter
                    presence_penalty=presence_penalty, # Penalize new topics (-2 to 2)
                    frequency_penalty=frequency_penalty, # Penalize repetition (-2 to 2)
                )
                return response.choices[0].message.content
            except Exception as e:
                attempt += 1
                if attempt >= max_retries:
                    raise Exception(f"Failed to get response from OpenAI after {max_retries} attempts: {str(e)}")
                print(f"API error: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    @staticmethod
    def generate_image(prompt: str, n: int = 1, size: str = "1024x1024", 
                       max_retries: int = 3, retry_delay: int = 2) -> list[str]:
        """
        Use OpenAI's Image API to generate images with error handling
        """
        # Ensure prompt isn't too long for the API
        if len(prompt) > 1000:
            prompt = prompt[:997] + "..."
            
        attempt = 0
        while attempt < max_retries:
            try:
                resp = openai.images.generate(
                    prompt=prompt,
                    n=n,
                    size=size
                )
                return [img.url for img in resp.data]
            except Exception as e:
                attempt += 1
                if attempt >= max_retries:
                    print(f"Failed to generate image after {max_retries} attempts: {str(e)}")
                    return []
                print(f"Image API error: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)


class Society:
    """Represents a society/faction that blobs can belong to"""
    def __init__(self, society_id: int, ideology: str, values: List[str]):
        self.society_id = society_id
        self.ideology = ideology
        self.values = values
        self.members: List[int] = []  # List of blob IDs belonging to this society
        self.relations: Dict[int, float] = {}  # Relations with other societies (-1.0 to 1.0)
        self.image_url: Optional[str] = None
    
    def __repr__(self):
        return f"Society-{self.society_id}(ideology='{self.ideology}', members={len(self.members)})"
    
    def add_member(self, blob_id: int):
        """Add a blob to this society"""
        if blob_id not in self.members:
            self.members.append(blob_id)
    
    def remove_member(self, blob_id: int):
        """Remove a blob from this society"""
        if blob_id in self.members:
            self.members.remove(blob_id)
    
    def update_relation(self, other_society_id: int, change: float):
        """Update relation with another society"""
        current = self.relations.get(other_society_id, 0.0)
        new_value = max(-1.0, min(1.0, current + change))  # Clamp between -1.0 and 1.0
        self.relations[other_society_id] = new_value


class Blob:
    """
    Represents an individual blob creature with personality and relationships
    """
    def __init__(self, blob_id: int, properties: Dict[str, Any]):
        self.blob_id = blob_id
        self.properties = properties
        self.name: str = f"Blob-{blob_id}"  # Default name
        self.society_id: Optional[int] = None  # Society this blob belongs to
        self.image_url: Optional[str] = None
        self.personality: str = ""
        self.traits: List[str] = []
        self.relationships: Dict[int, float] = {}  # Maps other blob_ids to relationship scores (-1.0 to 1.0)
        self.history: List[Dict[str, Any]] = []    # History of significant events for this blob
        
    def __repr__(self):
        society_info = f", society={self.society_id}" if self.society_id is not None else ""
        return f"Blob(id={self.blob_id}, name='{self.name}'{society_info})"

    def prompt_description(self) -> str:
        """
        Create a textual description based on the blob's properties.
        """
        parts = [f"{key}: {value}" for key, value in self.properties.items()]
        return "; ".join(parts)
    
    def add_event(self, year: int, event_type: str, description: str):
        """Record a significant event in this blob's history"""
        self.history.append({
            "year": year,
            "type": event_type,
            "description": description
        })
    
    def update_relationship(self, other_blob_id: int, change: float):
        """Update relationship score with another blob"""
        current = self.relationships.get(other_blob_id, 0.0)
        new_value = max(-1.0, min(1.0, current + change))  # Clamp between -1.0 and 1.0
        self.relationships[other_blob_id] = new_value
    
    def get_relationship_summary(self) -> str:
        """Get a summary of this blob's relationships"""
        if not self.relationships:
            return f"{self.name} has no established relationships yet."
        
        result = []
        for other_id, score in self.relationships.items():
            if score > 0.7:
                status = "close friend"
            elif score > 0.3:
                status = "friend"
            elif score > -0.3:
                status = "acquaintance"
            elif score > -0.7:
                status = "dislikes"
            else:
                status = "enemy"
            result.append(f"Relationship with Blob {other_id}: {status} ({score:.1f})")
        
        return "\n".join(result)
    
    def join_society(self, society_id: int):
        """Join a society"""
        self.society_id = society_id
    
    def leave_society(self):
        """Leave current society"""
        self.society_id = None


class WorldEvent:
    """
    Represents a significant event in the simulation
    """
    def __init__(self, year: int, headline: str, details: str, impacts: Dict[int, str]):
        self.year = year
        self.headline = headline
        self.details = details
        self.impacts = impacts  # Dict mapping blob_id to impact description
        self.image_url: Optional[str] = None
    
    def __repr__(self):
        return f"WorldEvent(year={self.year}, headline='{self.headline}')"
    
    def to_string(self) -> str:
        """Format the event for display"""
        impact_str = "\n".join([f"- {impact}" for blob_id, impact in self.impacts.items()])
        return f"Year {self.year}: {self.headline}\n{self.details}\n\nImpacts:\n{impact_str}"


class EnhancedGameState:
    """
    Enhanced game state with improved AI capabilities and event tracking
    """
    def __init__(self):
        self.blobs: List[Blob] = []
        self.societies: List[Society] = []
        self.message_history: List[Dict[str, str]] = []
        self.world_events: List[WorldEvent] = []
        self.current_blob_id = 0
        self.current_society_id = 0
        self.current_year = 0

        self.blob_image_generator = BlobImageGenerator(
            api_key=settings.openai_api_key,
            reference_image_path="local_blob_example.png"
        )
    
    def get_enhanced_system_prompt(self, num_blobs: int) -> Dict[str, str]:
        """
        Create an improved system prompt with clearer instructions
        """
        return {
            "role": "system",
            "content": (
                f"You are simulating a political evolution game in a fantasy world with {num_blobs} blob creatures. "
                f"Blobs are gelatinous beings with personalities, traits, and social connections. "
                f"They form societies based on shared values and ideologies.\n\n"
                f"SIMULATION RULES:\n"
                f"1. Maintain consistency with previous events and blob characteristics\n"
                f"2. Consider how blob personalities and society values affect decisions\n"
                f"3. Introduce realistic conflicts, friendships, and developments\n"
                f"4. Balance randomness with logical consequences\n\n"
                f"FORMAT YOUR RESPONSE AS:\n"
                f"[YEAR]: {self.current_year + 1}\n"
                f"[HEADLINE]: Brief headline of main event\n"
                f"[DETAILS]: Detailed description of what happened\n"
                f"[IMPACTS]: How this affects specific blobs and societies\n\n"
                f"Keep total response under 800 characters. Be creative but consistent."
            )
        }

    
    def generate_societies(self, num_societies: int) -> List[Society]:
        """Generate societies with distinct ideologies and values"""
        prompt = (
            f"Create {num_societies} distinct societies for a fantasy world of blob creatures. "
            f"For each society, provide:\n"
            f"1. A political/social ideology\n"
            f"2. Three core values\n\n"
            f"Format as JSON array with objects containing 'ideology', and 'values' fields."
        )
        
        messages = [
            {"role": "system", "content": "You create detailed fantasy societies in JSON format."},
            {"role": "user", "content": prompt}
        ]
        
        response = OpenAIClient.ask_gpt(messages, temperature=0.7)
        
        # Extract JSON from response
        json_match = re.search(r'\[\s*{.*}\s*\]', response, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
        else:
            # Fallback if proper JSON isn't found
            json_text = response
        
        try:
            society_data = json.loads(json_text)
        except json.JSONDecodeError:
            # If JSON parsing fails, create default societies
            print("Failed to parse society JSON. Creating default societies.")
            society_data = [
                {"ideology": "Unknown", "values": ["Survival", "Community", "Progress"]}
                for i in range(num_societies)
            ]
        
        societies = []
        for i, data in enumerate(society_data[:num_societies]):
            society = Society(
                society_id=i,
                ideology=data.get("ideology", "Unknown"),
                values=data.get("values", ["Unknown"])
            )
            societies.append(society)
        
        return societies
        
    def generate_blobs(self, num_blobs: int):
        """Generate random blobs with properties"""
        self.blobs = []
        self.current_blob_id = 0
        
        for i, props in enumerate(generate_random_blobs(num_samples=num_blobs)):
            blob = Blob(blob_id=self.current_blob_id, properties=props)
            self.blobs.append(blob)
            self.current_blob_id += 1
    
    def get_blobs_to_string(self) -> str:
        """Format blob information as a string"""
        return "\n".join(
            f"{b.name} (ID: {b.blob_id}): {b.prompt_description()}" for b in self.blobs
        )
    
    def get_societies_to_string(self) -> str:
        """Format society information as a string"""
        if not self.societies:
            return "No societies have formed yet."
            
        result = []
        for society in self.societies:
            members = [b for b in self.blobs if b.society_id == society.society_id]
            member_names = ", ".join([b.name for b in members]) if members else "None"
            
            result.append(
                f"Society-{society.society_id}\n"
                f"Ideology: {society.ideology}\n"
                f"Values: {', '.join(society.values)}\n"
                f"Members: {member_names}\n"
            )
        
        return "\n".join(result)
    
    def generate_blob_personality(self, blob: Blob) -> Tuple[str, List[str]]:
        """Generate a consistent personality profile and traits for a blob based on its properties"""
        prompt = (
            f"Based on these properties: {blob.prompt_description()}, "
            f"create for the blob named {blob.name}:\n"
            f"1. A brief personality description (100-150 characters)\n"
            f"2. A list of 3-5 distinct personality traits separated by commas\n\n"
            f"Format as: 'PERSONALITY: [description] | TRAITS: [trait1, trait2, ...]'"
        )
        
        messages = [
            {"role": "system", "content": "You create personalities for fantasy creatures."},
            {"role": "user", "content": prompt}
        ]
        
        response = OpenAIClient.ask_gpt(messages, temperature=0.7)
        
        # Parse the response
        personality = ""
        traits = []
        
        personality_match = re.search(r'PERSONALITY:\s*(.*?)\s*\|', response)
        if personality_match:
            personality = personality_match.group(1).strip()
        
        traits_match = re.search(r'TRAITS:\s*(.*)', response, re.DOTALL)
        if traits_match:
            traits_text = traits_match.group(1).strip()
            traits = [trait.strip() for trait in traits_text.split(',')]
        
        # Fallback in case parsing fails
        if not personality:
            personality = f"A mysterious blob with unique qualities"
        
        if not traits or len(traits) == 0:
            traits = ["mysterious", "adaptable", "curious"]
        
        return personality, traits

    def generate_blob_images(self):
        """Generate visual representations for each blob"""
        for blob in self.blobs:
            traits_str = ", ".join(blob.traits) if blob.traits else "mysterious personality"
            
            prompt = (
                f"A cute fantasy blob creature named {blob.name} with {traits_str}. "
                f"Characteristics: {blob.prompt_description()}. "
                f"Personality: {blob.personality}. "
                f"Make it colorful, gelatinous, with simple facial features. No text or labels."
            )
            
            urls = OpenAIClient.generate_image(prompt=prompt, n=1, size="512x512")
            if urls:
                blob.image_url = urls[0]
                print(f"Generated image for {blob.name}: {blob.image_url}")
    
    def generate_society_images(self):
        """Generate visual representations for each society"""
        for society in self.societies:
            values_str = ", ".join(society.values)
            
            prompt = (
                f"A symbolic representation of 'Society-{society.society_id}', a society of blob creatures. "
                f"Their ideology is {society.ideology} and they value {values_str}. "
                f"Create an abstract emblem or flag that represents their identity. No text."
            )
            
            urls = OpenAIClient.generate_image(prompt=prompt, n=1, size="512x512")
            if urls:
                society.image_url = urls[0]
                print(f"Generated image for Society-{society.society_id}: {society.image_url}")
    
    def assign_blobs_to_societies(self):
        """Assign blobs to societies based on compatibility"""
        if not self.societies or not self.blobs:
            return
            
        for blob in self.blobs:
            # Find most compatible society or leave unaffiliated (25% chance)
            if random.random() < 0.75:  # 75% chance to join a society
                # For now, just random assignment
                society_id = random.choice(self.societies).society_id
                blob.join_society(society_id)
                
                # Add blob to society's member list
                society = next((s for s in self.societies if s.society_id == society_id), None)
                if society:
                    society.add_member(blob.blob_id)
    
    def initialize_with_personalities(self, num_blobs: int, num_societies: int = 3):
        """Initialize game with blobs, personalities, and societies"""
        # Generate basic blobs
        self.generate_blobs(num_blobs)
        
        # Generate societies
        self.societies = self.generate_societies(num_societies)
        
        # Reset game state
        self.message_history = []
        self.world_events = []
        self.current_year = 0
        
        # Generate personalities for each blob
        for blob in self.blobs:
            personality, traits = self.generate_blob_personality(blob)
            blob.personality = personality
            blob.traits = traits
        
        # Assign blobs to societies
        self.assign_blobs_to_societies()
        
        # Add system prompt
        self.message_history.append(self.get_enhanced_system_prompt(num_blobs))
        
        # Add blob information to message history
        blob_info = self.get_blobs_to_string()
        personalities_str = "\n\n".join([
            f"{b.name}: {b.personality} (Traits: {', '.join(b.traits)})" for b in self.blobs
        ])
        
        societies_info = self.get_societies_to_string()
        
        self.message_history.append({
            "role": "user",
            "content": (
                f"Here are the blobs in our simulation:\n{blob_info}\n\n"
                f"Their personalities:\n{personalities_str}\n\n"
                f"Societies:\n{societies_info}\n\n"
                f"Begin the simulation in year 0 with an initial state of the world."
            )
        })
        
        # Generate images after initialization
        #self.generate_blob_images()
        #self.generate_society_images()
    
    def summarize_world_history(self, max_events: int = 3) -> str:
        """Create a summary of key historical events to maintain context"""
        if not self.world_events:
            return "No historical events have occurred yet."
        
        if len(self.world_events) <= max_events:
            events_to_show = self.world_events
        else:
            # Show first event for context, plus most recent events
            events_to_show = [self.world_events[0]] + self.world_events[-(max_events-1):]
        
        return "\n\n".join([event.to_string() for event in events_to_show])
    
    def parse_event_from_response(self, response: str) -> Optional[WorldEvent]:
        """Parse a structured event from the AI response"""
        try:
            # Extract year
            year_match = re.search(r"\[YEAR\]:\s*(\d+)", response)
            headline_match = re.search(r"\[HEADLINE\]:\s*(.*?)(\n|$)", response)
            details_match = re.search(r"\[DETAILS\]:\s*(.*?)(\n\[|$)", response, re.DOTALL)
            impacts_match = re.search(r"\[IMPACTS\]:\s*(.*?)($)", response, re.DOTALL)
            
            if not all([year_match, headline_match, details_match, impacts_match]):
                print("Failed to parse event structure from response.")
                return None
            
            year = int(year_match.group(1))
            headline = headline_match.group(1).strip()
            details = details_match.group(1).strip()
            impacts_text = impacts_match.group(1).strip()
            
            # Parse impacts - more flexible to account for different formatting
            impacts = {}
            for i, line in enumerate(impacts_text.split('\n')):
                # Try to match "Blob Name:" format
                blob_name_match = re.search(r"(.*?):\s*(.*)", line)
                # Try to match "- Blob ID:" format
                blob_id_match = re.search(r"Blob\s+(\d+):\s*(.*)", line)
                
                if blob_id_match:
                    blob_id = int(blob_id_match.group(1))
                    impact = blob_id_match.group(2).strip()
                    impacts[blob_id] = impact
                elif blob_name_match:
                    # Try to find blob by name
                    name = blob_name_match.group(1).strip()
                    impact = blob_name_match.group(2).strip()
                    
                    # Look up the blob by name
                    blob = next((b for b in self.blobs if b.name.lower() == name.lower()), None)
                    if blob:
                        impacts[blob.blob_id] = impact
                    else:
                        # Just use a placeholder ID for unrecognized names
                        impacts[100 + i] = f"{name}: {impact}"
            
            return WorldEvent(year, headline, details, impacts)
        
        except Exception as e:
            print(f"Error parsing event: {str(e)}")
            return None
    
    def run_iteration(self, temperature: float = 0.7) -> WorldEvent:
        """
        Run a game iteration with structured output and event parsing
        """
        # Add history summary if we have previous events
        if self.world_events:
            history_summary = self.summarize_world_history()
            self.message_history.append({
                "role": "system",
                "content": f"Recent world history:\n{history_summary}"
            })
        
        # Add format reminder to the prompt
        format_reminder = {
            "role": "user", 
            "content": (
                "Advance the simulation by one time period. Follow the required format exactly "
                "with [YEAR], [HEADLINE], [DETAILS], and [IMPACTS] sections. "
                "Make sure to include both individual blob interactions and society-level events."
            )
        }
        self.message_history.append(format_reminder)
        
        # Get response
        resp_text = OpenAIClient.ask_gpt(
            self.message_history, 
            temperature=temperature, 
            frequency_penalty=0.3
        )
        
        # Add response to message history
        self.message_history.append({"role": "assistant", "content": resp_text})
        
        # Parse the event
        event = self.parse_event_from_response(resp_text)
        
        if event:
            # Update game state
            self.current_year = event.year
            self.world_events.append(event)
            
            # Update blob relationships based on impacts
            self.update_relationships_from_event(event)
            
            # Generate an image for the event using our LLM-driven method
            image_url = self.generate_event_image(event)
            
            # Log the successful image generation
            if image_url:
                print(f"Successfully generated comic-style image for event: {event.headline}")
            
            return event
        else:
            print("Could not parse a valid event from the response")
            return None
    
    def update_relationships_from_event(self, event: WorldEvent):
        """Update blob relationships based on event impacts"""
        for blob_id, impact in event.impacts.items():
            impact_lower = impact.lower()
            
            # Skip invalid blob IDs
            blob = next((b for b in self.blobs if b.blob_id == blob_id), None)
            if not blob:
                continue
                
            # Check if this is a positive or negative impact
            is_positive = any(word in impact_lower for word in [
                "friend", "ally", "help", "support", "gift", "happy", "joy", "love"
            ])
            is_negative = any(word in impact_lower for word in [
                "enemy", "fight", "conflict", "anger", "hate", "sad", "hurt", "pain"
            ])
            
            # Look for mentions of other blobs (by name or ID)
            for other_blob in self.blobs:
                if other_blob.blob_id == blob_id:
                    continue
                
                if other_blob.name in impact or f"Blob {other_blob.blob_id}" in impact:
                    # Positive mention improves relationship, negative worsens it
                    relationship_change = 0.1 if is_positive else -0.1 if is_negative else 0.0
                    blob.update_relationship(other_blob.blob_id, relationship_change)
                    other_blob.update_relationship(blob_id, relationship_change)
                    
                    # Record this interaction in blob history
                    interaction_type = "positive" if is_positive else "negative" if is_negative else "neutral"
                    blob.add_event(event.year, interaction_type, 
                                  f"Interaction with {other_blob.name}: {impact}")
    
    def create_image_prompt(self, event: WorldEvent, previous_event: Optional[WorldEvent]) -> str:
        """
        Create a consistent image prompt based on reference blob style
        """
        # Use our new generator to create a consistent prompt
        return self.blob_image_generator.create_event_image_prompt(
            event_headline=event.headline,
            event_details=event.details
        )

    def generate_event_image(self, event: WorldEvent):
        """
        Generate a comic-style illustrative image for the event using consistent blob style
        """
        # Get previous event for context if it exists
        previous_event = None
        current_index = self.world_events.index(event) if event in self.world_events else -1
        
        if current_index > 0:
            previous_event = self.world_events[current_index - 1]
        
        # Create prompt for the image description
        prompt = self.create_image_prompt(event, previous_event)
        
        # Generate the image using our blob image generator
        urls = self.blob_image_generator.generate_image(
            prompt=prompt, 
            n=1, 
            size="1024x1024"
        )
        
        if urls:
            event.image_url = urls[0]
            print(f"Generated consistent blob-style image for event: {event.image_url}")
            return event.image_url
        return None
    
    def policy_proposition(self, proposal: str, temperature: float = 0.7) -> str:
        """Submit a user policy proposition to the simulation"""
        # Add proposal to message history
        self.message_history.append({
            "role": "user", 
            "content": f"POLICY PROPOSITION: {proposal}\n\nHow does this affect the world of blobs? Follow the required format."
        })
        
        # Get response
        resp_text = OpenAIClient.ask_gpt(self.message_history, temperature=temperature)
        self.message_history.append({"role": "assistant", "content": resp_text})
        
        # Parse the event
        event = self.parse_event_from_response(resp_text)
        if event:
            self.current_year = event.year
            self.world_events.append(event)
            self.update_relationships_from_event(event)
            
            # Use our LLM-driven image generation method
            image_url = self.generate_event_image(event)
            
            # Log the successful image generation
            if image_url:
                print(f"Successfully generated comic-style image for policy event: {event.headline}")
        
        return resp_text
    
    def get_world_status_report(self) -> str:
        """Generate a comprehensive status report of the world"""
        blob_names = ", ".join([b.name for b in self.blobs])
        society_ids = ", ".join([f"Society-{s.society_id}" for s in self.societies])
        
        prompt = (
            f"Create a brief status report on the current state of the blob world in year {self.current_year}. "
            f"Include:\n"
            f"1. The current situation of key blobs ({blob_names})\n"
            f"2. The status of the different societies ({society_ids})\n"
            f"3. Major ongoing friendships, conflicts, or developments\n"
            f"Keep it under 600 characters and focus on the most interesting elements."
        )
        
        self.message_history.append({"role": "user", "content": prompt})
        resp_text = OpenAIClient.ask_gpt(self.message_history, temperature=0.5)
        self.message_history.append({"role": "assistant", "content": resp_text})
        
        return resp_text

if __name__ == "__main__":
    # Example usage
    game_state = EnhancedGameState()
    
    # Initialize with 5 blobs and personalities
    print("Initializing game with 5 blobs...")
    game_state.initialize_with_personalities(5)
    
    # Run first iteration
    print("\nRunning first iteration...")
    event = game_state.run_iteration()
    if event:
        print(f"\nEvent: {event.headline}")
        print(f"Details: {event.details}")
        print("Impacts:")
        for blob_id, impact in event.impacts.items():
            print(f"- Blob {blob_id}: {impact}")
    
    # Submit a policy proposition
    print("\nSubmitting policy proposition...")
    #result = game_state.policy_proposition("A civil war breaks out due to wealth inequality.")
    #result = game_state.policy_proposition("Too much trash is piling up in the blob world.")
    result = game_state.policy_proposition("The blobs face a disagreemnt over blob hats and are building a huge wall.")
    print(f"Result: {result}...")
    
    # Run another iteration
    print("\nRunning another iteration...")
    event = game_state.run_iteration()
    if event:
        print(f"\nEvent: {event.headline}")
        print(f"Details: {event.details}")
    
    # Get world status report
    print("\nGenerating world status report...")
    status = game_state.get_world_status_report()
    print(f"Status: {status}")