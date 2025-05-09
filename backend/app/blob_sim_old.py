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

# Define relation change constants
RELATION_CHANGES = {
    "big_decrease": -0.25,
    "decrease": -0.1,
    "none": 0.0,
    "increase": 0.1,
    "big_increase": 0.25
}

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
                    model="gpt-4o-mini",
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
    
    def update_relation(self, other_society_id: int, change_type: str):
        """Update relation with another society based on change type"""
        if change_type not in RELATION_CHANGES:
            print(f"Warning: Invalid relation change type '{change_type}'")
            return
            
        # Initialize relation if it doesn't exist
        if other_society_id not in self.relations:
            # Start with neutral relation
            self.relations[other_society_id] = 0.0
            
        # Apply change
        delta = RELATION_CHANGES[change_type]
        current = self.relations[other_society_id]
        # Ensure relations stay within -1.0 to 1.0 range
        self.relations[other_society_id] = max(-1.0, min(1.0, current + delta))


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
    
    def join_society(self, society_id: int):
        """Join a society"""
        self.society_id = society_id


class WorldEvent:
    """
    Represents a significant event in the simulation
    """
    def __init__(self, year: int, headline: str, details: str, impacts: Dict[int, str], society_relations: Dict[str, str] = None):
        self.year = year
        self.headline = headline
        self.details = details
        self.impacts = impacts  # Dict mapping blob_id to impact description
        self.society_relations = society_relations or {}  # Dict mapping 'society_id1-society_id2' to relation change
        self.image_url: Optional[str] = None
    
    def __repr__(self):
        return f"WorldEvent(year={self.year}, headline='{self.headline}')"
    
    def to_string(self) -> str:
        """Format the event for display"""
        impact_str = "\n".join([f"- {impact}" for blob_id, impact in self.impacts.items()])
        
        # Add society relations if any exist
        relations_str = ""
        if self.society_relations:
            relations_list = []
            for key, change in self.society_relations.items():
                try:
                    society_ids = key.split('-')
                    if len(society_ids) == 2:
                        relations_list.append(f"Society-{society_ids[0]} and Society-{society_ids[1]}: {change}")
                except:
                    # Fallback for any parsing issues
                    relations_list.append(f"{key}: {change}")
                    
            if relations_list:
                relations_str = "\n\nSociety Relations:\n" + "\n".join([f"- {rel}" for rel in relations_list])
        
        return f"Year {self.year}: {self.headline}\n{self.details}\n\nImpacts:\n{impact_str}{relations_str}"


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
            api_key=settings.openai_api_key
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
                f"4. Balance randomness with logical consequences\n"
                f"5. Track how relations between societies change over time\n\n"
                f"RESPOND IN JSON FORMAT ONLY with the following structure:\n"
                f"```json\n"
                f"{{\n"
                f"  \"year\": {self.current_year + 1},\n"
                f"  \"headline\": \"Brief headline of main event\",\n"
                f"  \"details\": \"Detailed description of what happened\",\n"
                f"  \"impacts\": {{\n"
                f"    \"blob_1\": \"Impact on Blob-1\",\n"
                f"    \"blob_2\": \"Impact on Blob-2\"\n"
                f"  }},\n"
                f"  \"society_relations\": [\n"
                f"    {{\n"
                f"      \"society1\": 0,\n"
                f"      \"society2\": 1,\n"
                f"      \"change\": \"increase\"\n"
                f"    }}\n"
                f"  ]\n"
                f"}}\n"
                f"```\n\n"
                f"For society_relations, use only these change values: \"big_decrease\", \"decrease\", \"none\", \"increase\", or \"big_increase\".\n"
                f"Keep total response under 900 characters. Be creative but consistent. Return only valid JSON."
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
        
        # Initialize relations between societies
        for society in societies:
            for other_society in societies:
                if society.society_id != other_society.society_id:
                    # Start with a neutral relationship (0.0)
                    society.relations[other_society.society_id] = 0.0
        
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
            
            # Add relations information
            relations_info = []
            for other_id, relation_score in society.relations.items():
                # Convert score to a human-readable description
                relation_desc = "Neutral"
                if relation_score >= 0.75:
                    relation_desc = "Allied"
                elif relation_score >= 0.4:
                    relation_desc = "Friendly"
                elif relation_score >= 0.1:
                    relation_desc = "Positive"
                elif relation_score <= -0.75:
                    relation_desc = "Hostile"
                elif relation_score <= -0.4:
                    relation_desc = "Unfriendly"
                elif relation_score <= -0.1:
                    relation_desc = "Tense"
                
                relations_info.append(f"  - With Society-{other_id}: {relation_desc} ({relation_score:.1f})")
            
            relations_str = "\n".join(relations_info) if relations_info else "  None"
            
            result.append(
                f"Society-{society.society_id}\n"
                f"Ideology: {society.ideology}\n"
                f"Values: {', '.join(society.values)}\n"
                f"Members: {member_names}\n"
                f"Relations:\n{relations_str}\n"
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
            # Try to find and extract JSON from the response
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without code blocks
                json_match = re.search(r'(\{.*\})', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # No JSON found
                    print("No JSON found in response")
                    return None
            
            try:
                # Parse the JSON
                event_data = json.loads(json_str)
                
                # Extract the basic event data
                year = int(event_data.get('year', self.current_year + 1))
                headline = event_data.get('headline', 'Unknown Event')
                details = event_data.get('details', 'No details available')
                
                # Extract impacts
                impacts = {}
                impact_data = event_data.get('impacts', {})
                for key, value in impact_data.items():
                    # Try to extract blob ID from keys like "blob_1" or "Blob-2"
                    blob_id_match = re.search(r'blob[_-]?(\d+)', key.lower())
                    if blob_id_match:
                        blob_id = int(blob_id_match.group(1))
                        impacts[blob_id] = value
                    else:
                        # Try to find blob by name
                        blob = next((b for b in self.blobs if b.name.lower() == key.lower()), None)
                        if blob:
                            impacts[blob.blob_id] = value
                        else:
                            # Just use a placeholder ID for unrecognized names
                            impacts[hash(key) % 1000 + 100] = f"{key}: {value}"
                
                # Extract society relations
                society_relations = {}
                relations_data = event_data.get('society_relations', [])
                for relation in relations_data:
                    society1 = relation.get('society1')
                    society2 = relation.get('society2')
                    change_type = relation.get('change', 'none')
                    
                    # Skip invalid entries
                    if society1 is None or society2 is None:
                        continue
                        
                    # Normalize change type
                    if "big_decrease" in change_type:
                        change_type = "big_decrease"
                    elif "decrease" in change_type:
                        change_type = "decrease"
                    elif "none" in change_type or "neutral" in change_type:
                        change_type = "none"
                    elif "big_increase" in change_type:
                        change_type = "big_increase"
                    elif "increase" in change_type:
                        change_type = "increase"
                    else:
                        # Default to no change if we can't parse
                        change_type = "none"
                    
                    # Store relation change
                    relation_key = f"{society1}-{society2}"
                    society_relations[relation_key] = change_type
                
                return WorldEvent(year, headline, details, impacts, society_relations)
            
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {str(e)}")
                return None
        
        except Exception as e:
            print(f"Error parsing event: {str(e)}")
            # Fallback to the old parsing method if JSON parsing fails
            try:
                # Extract year
                year_match = re.search(r"\[YEAR\]:\s*(\d+)", response)
                headline_match = re.search(r"\[HEADLINE\]:\s*(.*?)(\n|$)", response)
                details_match = re.search(r"\[DETAILS\]:\s*(.*?)(\n\[|$)", response, re.DOTALL)
                impacts_match = re.search(r"\[IMPACTS\]:\s*(.*?)(\n\[|$)", response, re.DOTALL)
                relations_match = re.search(r"\[RELATIONS\]:\s*(.*?)($)", response, re.DOTALL)
                
                if not all([year_match, headline_match, details_match, impacts_match]):
                    print("Failed to parse event structure from response.")
                    return None
                
                year = int(year_match.group(1))
                headline = headline_match.group(1).strip()
                details = details_match.group(1).strip()
                impacts_text = impacts_match.group(1).strip()
                
                # Relations is optional, so we check if it exists
                relations_text = ""
                if relations_match:
                    relations_text = relations_match.group(1).strip()
                
                # Parse impacts
                impacts = {}
                for i, line in enumerate(impacts_text.split('\n')):
                    blob_name_match = re.search(r"(.*?):\s*(.*)", line)
                    blob_id_match = re.search(r"Blob\s+(\d+):\s*(.*)", line)
                    
                    if blob_id_match:
                        blob_id = int(blob_id_match.group(1))
                        impact = blob_id_match.group(2).strip()
                        impacts[blob_id] = impact
                    elif blob_name_match:
                        name = blob_name_match.group(1).strip()
                        impact = blob_name_match.group(2).strip()
                        
                        blob = next((b for b in self.blobs if b.name.lower() == name.lower()), None)
                        if blob:
                            impacts[blob.blob_id] = impact
                        else:
                            impacts[100 + i] = f"{name}: {impact}"
                
                # Parse society relations
                society_relations = {}
                if relations_text:
                    for line in relations_text.split('\n'):
                        relation_match = re.search(r"Society-(\d+)\s+and\s+Society-(\d+):\s*(.*)", line)
                        
                        if relation_match:
                            society1 = int(relation_match.group(1))
                            society2 = int(relation_match.group(2))
                            change_type = relation_match.group(3).strip().lower()
                            
                            # Normalize change type
                            if "big_decrease" in change_type:
                                change_type = "big_decrease"
                            elif "decrease" in change_type:
                                change_type = "decrease"
                            elif "none" in change_type or "neutral" in change_type:
                                change_type = "none"
                            elif "big_increase" in change_type:
                                change_type = "big_increase"
                            elif "increase" in change_type:
                                change_type = "increase"
                            else:
                                change_type = "none"
                            
                            relation_key = f"{society1}-{society2}"
                            society_relations[relation_key] = change_type
                
                return WorldEvent(year, headline, details, impacts, society_relations)
            
            except Exception as nested_e:
                print(f"Fallback parsing also failed: {str(nested_e)}")
                return None
    
    def update_society_relations(self, event: WorldEvent):
        """Update society relations based on the event's relationship changes"""
        if not event.society_relations:
            return
            
        print(f"Updating society relations for event: {event.headline}")
        
        for relation_key, change_type in event.society_relations.items():
            try:
                # Parse society IDs from the key (format: "society1-society2")
                society_ids = relation_key.split('-')
                if len(society_ids) != 2:
                    continue
                    
                society1_id = int(society_ids[0])
                society2_id = int(society_ids[1])
                
                # Get the societies
                society1 = next((s for s in self.societies if s.society_id == society1_id), None)
                society2 = next((s for s in self.societies if s.society_id == society2_id), None)
                
                if society1 and society2:
                    # Update relations for both societies
                    old_relation1 = society1.relations.get(society2_id, 0.0)
                    old_relation2 = society2.relations.get(society1_id, 0.0)
                    
                    society1.update_relation(society2_id, change_type)
                    society2.update_relation(society1_id, change_type)
                    
                    # Log the changes
                    print(f"  Society-{society1_id} and Society-{society2_id} relation: {old_relation1:.2f} -> {society1.relations[society2_id]:.2f} ({change_type})")
            except Exception as e:
                print(f"Error updating relation for {relation_key}: {str(e)}")
    
    def run_iteration(self, temperature: float = 0.7, create_image=True) -> WorldEvent:
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
                "Advance the simulation by one time period. Return your response as a JSON object "
                "with fields for year, headline, details, impacts, and society_relations. "
                "For society_relations, include how relations between societies change "
                "(big_decrease, decrease, none, increase, or big_increase) based on the events."
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
            
            # Update society relations based on the event
            self.update_society_relations(event)
            
            if create_image:
                # Generate an image for the event using our LLM-driven method
                image_url = self.generate_event_image(event)
                
                # Log the successful image generation
                if image_url:
                    print(f"Successfully generated comic-style image for event: {event.headline}")
            
            return event
        else:
            print("Could not parse a valid event from the response")
            return None
    
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
            "content": (
                f"POLICY PROPOSITION: {proposal}\n\n"
                f"How does this affect the world of blobs? Return your response as a JSON object "
                f"with fields for year, headline, details, impacts, and society_relations."
            )
        })
        
        # Get response
        resp_text = OpenAIClient.ask_gpt(self.message_history, temperature=temperature)
        self.message_history.append({"role": "assistant", "content": resp_text})
        
        # Parse the event
        event = self.parse_event_from_response(resp_text)
        if event:
            self.current_year = event.year
            self.world_events.append(event)
            
            # Update society relations based on the event
            self.update_society_relations(event)
            
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
            f"4. The current relations between societies\n"
            f"Keep it under 700 characters and focus on the most interesting elements."
        )
        
        self.message_history.append({"role": "user", "content": prompt})
        resp_text = OpenAIClient.ask_gpt(self.message_history, temperature=0.5)
        self.message_history.append({"role": "assistant", "content": resp_text})
        
        return resp_text

    def get_society_relations_report(self) -> str:
        """Generate a specific report about current society relations"""
        if not self.societies:
            return "No societies exist in the simulation."
            
        relations_status = []
        for i, society1 in enumerate(self.societies):
            for j, society2 in enumerate(self.societies):
                if i < j:  # Only process each pair once
                    relation = society1.relations.get(society2.society_id, 0.0)
                    
                    # Get a qualitative description
                    description = "Neutral"
                    if relation >= 0.75:
                        description = "Allied"
                    elif relation >= 0.4:
                        description = "Friendly"
                    elif relation >= 0.1:
                        description = "Positive"
                    elif relation <= -0.75:
                        description = "Hostile"
                    elif relation <= -0.4:
                        description = "Unfriendly"
                    elif relation <= -0.1:
                        description = "Tense"
                    
                    relations_status.append(
                        f"Society-{society1.society_id} ({society1.ideology}) and "
                        f"Society-{society2.society_id} ({society2.ideology}): {description} ({relation:.2f})"
                    )
        
        return "Current Society Relations:\n" + "\n".join([f"- {rel}" for rel in relations_status])

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
        print("Society Relations:")
        for relation_key, change in event.society_relations.items():
            print(f"- {relation_key}: {change}")
    
    # Submit a policy proposition
    print("\nSubmitting policy proposition...")
    result = game_state.policy_proposition("A civil war breaks out due to wealth inequality.")
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
    
    # Get society relations report
    print("\nGenerating society relations report...")
    relations = game_state.get_society_relations_report()
    print(f"Relations: {relations}")