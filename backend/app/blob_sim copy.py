import openai
import re
import json
import time
import random
from typing import List, Dict, Any, Optional, Tuple
from config import settings
from random_stats import generate_random_blobs

openai.api_key = settings.openai_api_key

class AIHelper:
    """Simple wrapper for OpenAI API calls"""
    
    @staticmethod
    def ask_ai(messages: list, temperature: float = 0.7, max_retries: int = 3) -> str:
        """Send a message to OpenAI API and get a response"""
        attempt = 0
        while attempt < max_retries:
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=temperature,
                )
                return response.choices[0].message.content
            except Exception as e:
                attempt += 1
                if attempt >= max_retries:
                    raise Exception(f"Failed to get response after {max_retries} attempts: {str(e)}")
                print(f"Error: {str(e)}. Trying again in 2 seconds...")
                time.sleep(2)
    
    @staticmethod
    def generate_image(prompt: str, n: int = 1, size: str = "1024x1024") -> list[str]:
        """Generate images with the OpenAI API"""
        # Make sure prompt isn't too long
        if len(prompt) > 1000:
            prompt = prompt[:997] + "..."
            
        try:
            resp = openai.images.generate(
                prompt=prompt,
                n=n,
                size=size
            )
            return [img.url for img in resp.data]
        except Exception as e:
            print(f"Couldn't create image: {str(e)}")
            return []


class BlobGroup:
    """A group of blob creatures that work together"""
    def __init__(self, group_id: int, name: str, structure: str, traits: List[str]):
        self.group_id = group_id
        self.name = name
        self.structure = structure
        self.traits = traits
        self.members = []  # List of blob IDs in this group
        self.relationships = {}  # How this group feels about other groups (-1.0 to 1.0)
        self.image_url = None
        self.stats = {
            "unity": random.uniform(40.0, 90.0),
            "efficiency": random.uniform(30.0, 80.0),
            "growth": random.uniform(10.0, 50.0),
            "advancement": random.uniform(5.0, 40.0)
        }
    
    def __str__(self):
        return f"Group-{self.group_id}('{self.name}', members={len(self.members)})"
    
    def add_member(self, blob_id: int):
        """Add a blob to this group"""
        if blob_id not in self.members:
            self.members.append(blob_id)
    
    def remove_member(self, blob_id: int):
        """Remove a blob from this group"""
        if blob_id in self.members:
            self.members.remove(blob_id)
    
    def update_relationship(self, other_group_id: int, change: float):
        """Change how this group feels about another group"""
        current = self.relationships.get(other_group_id, 0.0)
        new_value = max(-1.0, min(1.0, current + change))
        self.relationships[other_group_id] = new_value
    
    def update_stats(self):
        """Update group stats over time"""
        # Consider how many members we have
        member_factor = min(1.0, len(self.members) / 5.0)
        
        # Change stats by small random amounts
        self.stats["unity"] += random.uniform(-8.0, 5.0)
        self.stats["efficiency"] += random.uniform(-3.0, 6.0) * member_factor
        self.stats["growth"] += random.uniform(-2.0, 8.0) * member_factor
        self.stats["advancement"] += random.uniform(0.0, 4.0) * member_factor
        
        # Make sure stats stay between 0 and 100
        for stat in self.stats:
            self.stats[stat] = max(0.0, min(100.0, self.stats[stat]))


class Blob:
    """A single blob creature with its own traits and behaviors"""
    def __init__(self, blob_id: int, features: Dict[str, Any]):
        self.blob_id = blob_id
        self.features = features
        self.group_id = None  # Which group this blob belongs to
        self.image_url = None
        self.behavior = ""
        self.traits = []
        self.relationships = {}  # How this blob feels about other blobs (-1.0 to 1.0)
        self.history = []  # Important things that happened to this blob
        self.stats = {
            "energy": random.uniform(60.0, 100.0),
            "health": random.uniform(40.0, 100.0),
            "social": random.uniform(10.0, 50.0),
            "learning": random.uniform(20.0, 80.0)
        }
        
    def __str__(self):
        group_info = f", group={self.group_id}" if self.group_id is not None else ""
        return f"Blob-{self.blob_id}({group_info})"

    def get_description(self) -> str:
        """Create a text description of this blob"""
        parts = [f"{key}: {value}" for key, value in self.features.items()]
        return "; ".join(parts)
    
    def add_to_history(self, year: int, event_type: str, description: str):
        """Record something important that happened to this blob"""
        self.history.append({
            "year": year,
            "type": event_type,
            "description": description
        })
    
    def update_relationship(self, other_blob_id: int, change: float):
        """Change how this blob feels about another blob"""
        current = self.relationships.get(other_blob_id, 0.0)
        new_value = max(-1.0, min(1.0, current + change))
        self.relationships[other_blob_id] = new_value
    
    def get_relationship_info(self) -> str:
        """Get information about this blob's relationships with others"""
        if not self.relationships:
            return f"Blob-{self.blob_id} doesn't have any relationships yet."
        
        result = []
        for other_id, score in self.relationships.items():
            if score > 0.7:
                status = "loves"
            elif score > 0.3:
                status = "likes"
            elif score > -0.3:
                status = "neutral toward"
            elif score > -0.7:
                status = "dislikes"
            else:
                status = "strongly dislikes"
            result.append(f"Relationship with Blob-{other_id}: {status} ({score:.2f})")
        
        return "\n".join(result)
    
    def update_stats(self):
        """Update this blob's stats over time"""
        # Change stats by small random amounts
        self.stats["energy"] += random.uniform(-5.0, 5.0)
        self.stats["health"] += random.uniform(-3.0, 3.0)
        self.stats["social"] += random.uniform(-2.0, 4.0)
        self.stats["learning"] += random.uniform(-1.0, 2.0)
        
        # Make sure stats stay between 0 and 100
        for stat in self.stats:
            self.stats[stat] = max(0.0, min(100.0, self.stats[stat]))
    
    def join_group(self, group_id: int):
        """Join a group"""
        self.group_id = group_id
    
    def leave_group(self):
        """Leave current group"""
        self.group_id = None


class WorldEvent:
    """Something important that happened in the blob world"""
    def __init__(self, time: int, name: str, description: str, effects: Dict[int, str]):
        self.time = time
        self.name = name
        self.description = description
        self.effects = effects  # How this event affected specific blobs
        self.image_url = None
        self.importance = {
            "impact": random.uniform(0.1, 1.0),
            "range": random.uniform(1.0, 10.0),
            "duration": random.uniform(0.5, 5.0)
        }
    
    def __str__(self):
        return f"Event(time={self.time}, name='{self.name}')"
    
    def full_description(self) -> str:
        """Get the complete description of this event"""
        impact_str = "\n".join([f"- Blob-{blob_id}: {effect}" for blob_id, effect in self.effects.items()])
        return f"Time={self.time} | {self.name}\n{self.description}\n\nEffects:\n{impact_str}"


class BlobWorld:
    """The world where all the blobs live and interact"""
    def __init__(self):
        self.blobs = []
        self.groups = []
        self.messages = []
        self.events = []
        self.next_blob_id = 0
        self.next_group_id = 0
        self.current_time = 0
        self.world_conditions = {
            "food": 0.7,       # How much food is available (0.0 to 1.0)
            "safety": 0.8,     # How safe the environment is (0.0 to 1.0)
            "change": 0.05,    # How fast things change (0.0 to 1.0)
            "social": 0.4      # How often blobs interact (0.0 to 1.0)
        }
        self.stats = {
            "groups_formed": 0,
            "groups_broken": 0,
            "friendly_meetings": 0,
            "unfriendly_meetings": 0,
            "neutral_meetings": 0,
            "food_shortages": 0,
            "environment_changes": 0
        }
    
    def get_system_prompt(self, num_blobs: int) -> Dict[str, str]:
        """Create instructions for the AI"""
        return {
            "role": "system",
            "content": (
                f"You are telling a story about a world with {num_blobs} blob creatures. "
                f"These are simple, cute creatures with different traits that determine how they behave "
                f"and interact. They form into groups.\n\n"
                f"STORY GUIDELINES:\n"
                f"1. Be consistent with what happened before\n"
                f"2. Consider food, safety, and other environmental factors\n"
                f"3. Show how blobs interact and form relationships\n"
                f"4. Base what happens on the blobs' traits\n\n"
                f"FORMAT YOUR RESPONSE LIKE THIS:\n"
                f"[TIME]: {self.current_time + 1}\n"
                f"[EVENT]: Brief name of what happened\n"
                f"[STORY]: Detailed description of what happened\n"
                f"[EFFECTS]: How this affected specific blobs and groups\n\n"
                f"Keep your response under 800 characters. Focus on making a fun, interesting story."
            )
        }

    def get_blob_info(self) -> str:
        """Get information about all the blobs"""
        return "\n".join(
            f"Blob-{b.blob_id}: Features={b.get_description()}" for b in self.blobs
        )
    
    def get_group_info(self) -> str:
        """Get information about all the groups"""
        if not self.groups:
            return "No groups have formed yet."
            
        result = []
        for group in self.groups:
            members = [b for b in self.blobs if b.group_id == group.group_id]
            member_ids = ", ".join([str(b.blob_id) for b in members]) if members else "None"
            
            result.append(
                f"Group-{group.group_id}: {group.name}\n"
                f"Structure: {group.structure}\n"
                f"Traits: {', '.join(group.traits)}\n"
                f"Members: {member_ids}\n"
                f"Stats: {', '.join([f'{k}={v:.2f}' for k,v in group.stats.items()])}\n"
            )
        
        return "\n".join(result)
    
    def create_blob_behavior(self, blob: Blob) -> Tuple[str, List[str]]:
        """Figure out how a blob behaves based on its features"""
        prompt = (
            f"Based on these features: {blob.get_description()}, "
            f"for Blob-{blob.blob_id}:\n"
            f"1. Write a short, simple description of how this blob typically behaves (100-150 chars)\n"
            f"2. List 3-5 personality traits separated by commas\n\n"
            f"Format as: 'BEHAVIOR: [description] | TRAITS: [trait1, trait2, ...]'"
        )
        
        messages = [
            {"role": "system", "content": "You create fun, simple descriptions of blob creatures."},
            {"role": "user", "content": prompt}
        ]
        
        response = AIHelper.ask_ai(messages, temperature=0.7)
        
        # Get the behavior and traits from the response
        behavior = ""
        traits = []
        
        behavior_match = re.search(r'BEHAVIOR:\s*(.*?)\s*\|', response)
        if behavior_match:
            behavior = behavior_match.group(1).strip()
        
        traits_match = re.search(r'TRAITS:\s*(.*)', response, re.DOTALL)
        if traits_match:
            traits_text = traits_match.group(1).strip()
            traits = [trait.strip() for trait in traits_text.split(',')]
        
        # Default values if we couldn't parse the response
        if not behavior:
            behavior = f"A typical blob that responds to its environment"
        
        if not traits or len(traits) == 0:
            traits = ["friendly", "curious", "hungry"]
        
        return behavior, traits
    
    def create_groups(self, num_groups: int) -> List[BlobGroup]:
        """Create different groups for blobs to join"""
        prompt = (
            f"Create {num_groups} fun, different groups for a world of blob creatures. "
            f"For each group, give me:\n"
            f"1. A fun, creative name for the group\n"
            f"2. How the group is organized (like 'Family Unit', 'Wandering Tribe', etc.)\n"
            f"3. Three main traits that define the group\n\n"
            f"Format as JSON array with objects containing 'name', 'structure', and 'traits' fields."
        )
        
        messages = [
            {"role": "system", "content": "You create fun content about blob creatures."},
            {"role": "user", "content": prompt}
        ]
        
        response = AIHelper.ask_ai(messages, temperature=0.7)
        
        # Try to find JSON in the response
        json_match = re.search(r'\[\s*{.*}\s*\]', response, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
        else:
            json_text = response
        
        try:
            group_data = json.loads(json_text)
        except json.JSONDecodeError:
            # If we can't parse the JSON, create default groups
            print("Couldn't understand group data. Creating default groups.")
            group_data = [
                {"name": f"Blob Group {i}", "structure": "Simple Community", 
                 "traits": ["Friendly", "Helpful", "Curious"]}
                for i in range(num_groups)
            ]
        
        groups = []
        for i, data in enumerate(group_data[:num_groups]):
            group = BlobGroup(
                group_id=i,
                name=data.get("name", f"Blob Group {i}"),
                structure=data.get("structure", "Simple Community"),
                traits=data.get("traits", ["Friendly", "Helpful", "Curious"])
            )
            groups.append(group)
        
        return groups
    
    def create_blobs(self, num_blobs: int):
        """Create random blobs with different features"""
        self.blobs = []
        self.next_blob_id = 0
        
        for features in generate_random_blobs(num_samples=num_blobs):
            blob = Blob(blob_id=self.next_blob_id, features=features)
            self.blobs.append(blob)
            self.next_blob_id += 1
    
    def assign_blobs_to_groups(self):
        """Put blobs into groups based on compatibility"""
        if not self.groups or not self.blobs:
            return
            
        for blob in self.blobs:
            # There's a 75% chance a blob will join a group if interactions are frequent
            if random.random() < 0.75 * self.world_conditions["social"]:
                # For now, randomly assign to a group
                group_id = random.choice(self.groups).group_id
                blob.join_group(group_id)
                
                # Add blob to the group's member list
                group = next((g for g in self.groups if g.group_id == group_id), None)
                if group:
                    group.add_member(blob.blob_id)
    
    def setup_world(self, num_blobs: int, num_groups: int = 3):
        """Set up the blob world with blobs and groups"""
        # Create blobs
        self.create_blobs(num_blobs)
        
        # Create groups
        self.groups = self.create_groups(num_groups)
        
        # Reset world state
        self.messages = []
        self.events = []
        self.current_time = 0
        self.stats = {key: 0 for key in self.stats}
        
        # Determine behavior for each blob
        for blob in self.blobs:
            behavior, traits = self.create_blob_behavior(blob)
            blob.behavior = behavior
            blob.traits = traits
        
        # Assign blobs to groups
        self.assign_blobs_to_groups()
        
        # Add system prompt
        self.messages.append(self.get_system_prompt(num_blobs))
        
        # Add blob information
        blob_info = self.get_blob_info()
        behaviors_str = "\n\n".join([
            f"Blob-{b.blob_id}: {b.behavior} (Traits: {', '.join(b.traits)})" for b in self.blobs
        ])
        
        group_info = self.get_group_info()
        
        self.messages.append({
            "role": "user",
            "content": (
                f"Initial world state at Time=0:\n\n"
                f"Blobs:\n{blob_info}\n\n"
                f"Behaviors:\n{behaviors_str}\n\n"
                f"Groups:\n{group_info}\n\n"
                f"World conditions: {', '.join([f'{k}={v:.2f}' for k,v in self.world_conditions.items()])}\n\n"
                f"Start the story at time 0, describing the initial state of the blob world."
            )
        })
    
    def get_recent_events(self, max_events: int = 3) -> str:
        """Get a summary of recent important events"""
        if not self.events:
            return "No important events have happened yet."
        
        if len(self.events) <= max_events:
            events_to_show = self.events
        else:
            # Show first event for context, plus most recent events
            events_to_show = [self.events[0]] + self.events[-(max_events-1):]
        
        return "\n\n".join([event.full_description() for event in events_to_show])
    
    def parse_event(self, response: str) -> Optional[WorldEvent]:
        """Parse an event from the AI's response"""
        try:
            # Find the time, event name, story, and effects
            time_match = re.search(r"\[TIME\]:\s*(\d+)", response)
            event_match = re.search(r"\[EVENT\]:\s*(.*?)(\n|$)", response)
            story_match = re.search(r"\[STORY\]:\s*(.*?)(\n\[|$)", response, re.DOTALL)
            effects_match = re.search(r"\[EFFECTS\]:\s*(.*?)($)", response, re.DOTALL)
            
            if not all([time_match, event_match, story_match, effects_match]):
                print("Couldn't understand the event structure from the response.")
                return None
            
            time = int(time_match.group(1))
            event_name = event_match.group(1).strip()
            story = story_match.group(1).strip()
            effects_text = effects_match.group(1).strip()
            
            # Parse effects
            effects = {}
            for i, line in enumerate(effects_text.split('\n')):
                # Try to match "Blob-X:" or similar formats
                blob_match = re.search(r"Blob[- ](\d+):\s*(.*)", line, re.IGNORECASE)
                
                if blob_match:
                    blob_id = int(blob_match.group(1))
                    effect = blob_match.group(2).strip()
                    effects[blob_id] = effect
                else:
                    # Generic effect without a specific blob ID
                    effects[100 + i] = line.strip()
            
            return WorldEvent(time, event_name, story, effects)
        
        except Exception as e:
            print(f"Error parsing event: {str(e)}")
            return None
    
    def update_everything(self):
        """Update all blobs and groups for this time step"""
        # Update all blobs
        for blob in self.blobs:
            blob.update_stats()
            
        # Update all groups
        for group in self.groups:
            group.update_stats()
    
    def advance_story(self, temperature: float = 0.7) -> WorldEvent:
        """
        Move the story forward one step
        """
        # Slightly change world conditions each time
        for condition in self.world_conditions:
            delta = random.uniform(-0.05, 0.05)
            self.world_conditions[condition] = max(0.0, min(1.0, self.world_conditions[condition] + delta))
        
        # Add recent events summary if we have previous events
        if self.events:
            history_summary = self.get_recent_events()
            self.messages.append({
                "role": "system",
                "content": f"Recent events:\n{history_summary}\n\nCurrent world conditions: {', '.join([f'{k}={v:.2f}' for k,v in self.world_conditions.items()])}"
            })
        
        # Remind the AI how to format the response
        format_reminder = {
            "role": "user", 
            "content": (
                "Continue the story by moving forward one time step. Follow the format exactly "
                "with [TIME], [EVENT], [STORY], and [EFFECTS] sections. "
                "Include both individual blob stories and group dynamics. Make it interesting!"
            )
        }
        self.messages.append(format_reminder)
        
        # Get response from AI
        response = AIHelper.ask_ai(
            self.messages, 
            temperature=temperature
        )
        
        # Add response to message history
        self.messages.append({"role": "assistant", "content": response})
        
        # Parse the event
        event = self.parse_event(response)
        
        if event:
            # Update world state
            self.current_time = event.time
            self.events.append(event)
            
            # Update blob relationships based on effects
            self.update_relationships_from_event(event)
            
            # Update all blobs and groups
            self.update_everything()
            
            # Generate an image for the event
            #self.generate_event_image(event)
            
            return event
        else:
            print("Couldn't understand the event from the response")
            return None
    
    def update_relationships_from_event(self, event: WorldEvent):
        """Update blob relationships based on event effects"""
        for blob_id, effect in event.effects.items():
            effect_lower = effect.lower()
            
            # Skip invalid blob IDs
            blob = next((b for b in self.blobs if b.blob_id == blob_id), None)
            if not blob:
                continue
                
            # Check if this is a positive or negative effect
            is_positive = any(word in effect_lower for word in [
                "happy", "gain", "found", "improved", "better", "enjoyed", "helped"
            ])
            is_negative = any(word in effect_lower for word in [
                "sad", "lost", "hurt", "damaged", "worse", "scared", "angry"
            ])
            
            # Track statistics
            if is_positive:
                self.stats["friendly_meetings"] += 1
            elif is_negative:
                self.stats["unfriendly_meetings"] += 1
            else:
                self.stats["neutral_meetings"] += 1
            
            # Look for mentions of other blobs
            for other_blob in self.blobs:
                if other_blob.blob_id == blob_id:
                    continue
                
                if f"Blob-{other_blob.blob_id}" in effect or f"Blob {other_blob.blob_id}" in effect:
                    # Calculate relationship change based on effect type
                    relationship_change = 0.1 if is_positive else -0.1 if is_negative else 0.0
                    blob.update_relationship(other_blob.blob_id, relationship_change)
                    other_blob.update_relationship(blob_id, relationship_change)
                    
                    # Record this interaction
                    interaction_type = "positive" if is_positive else "negative" if is_negative else "neutral"
                    blob.add_to_history(event.time, interaction_type, 
                                     f"Interaction with Blob-{other_blob.blob_id}: {effect}")
    
    def generate_event_image(self, event: WorldEvent):
        """Generate a picture of the event with cute blob creatures"""
        prompt = (
            f"Illustration of blob creatures during: {event.name}. "
            f"Story: {event.description}. "
            f"Create cute, round, funny-looking blob creatures with simple faces and colorful bodies. "
            f"The blobs should be gelatinous, jiggly, and expressive. "
            f"Focus on the central part of the image with clear, simple details. "
            f"Playful, child-friendly style with vibrant colors. No text or labels."
        )
        
        urls = AIHelper.generate_image(prompt=prompt, n=1, size="512x512")
        if urls:
            event.image_url = urls[0]
            print(f"Created picture for event: {event.image_url}")
    
    def make_change(self, change_description: str, temperature: float = 0.7) -> str:
        """Make a change to the world and see what happens"""
        # Add change to message history
        self.messages.append({
            "role": "user", 
            "content": f"SOMETHING CHANGES: {change_description}\n\nHow does this affect the blob world? Follow the required format."
        })
        
        # Get response from AI
        response = AIHelper.ask_ai(self.messages, temperature=temperature)
        self.messages.append({"role": "assistant", "content": response})
        
        # Parse the event
        event = self.parse_event(response)
        if event:
            self.current_time = event.time
            self.events.append(event)
            self.update_relationships_from_event(event)
            self.update_everything()
            #self.generate_event_image(event)
        
        return response
    
    def get_world_report(self) -> str:
        """Get a report on the current state of the blob world"""
        group_names = ", ".join([f"Group-{g.group_id}" for g in self.groups])
        
        prompt = (
            f"Create a fun report about the current state of the blob world at Time={self.current_time}. "
            f"Include:\n"
            f"1. What's happening in the blob world overall\n"
            f"2. How the different groups are doing: {group_names}\n"
            f"3. Any interesting blob relationships or stories\n"
            f"4. How the world conditions are affecting everyone\n"
            f"Keep it under 600 characters and make it fun to read!"
        )
        
        self.messages.append({"role": "user", "content": prompt})
        response = AIHelper.ask_ai(self.messages, temperature=0.5)
        self.messages.append({"role": "assistant", "content": response})
        
        return response
    
    def blob_relationship_story(self, blob1_id: int, blob2_id: int, scenario: str = None) -> str:
        """Create a story about two blobs interacting"""
        # Find the blobs
        blob1 = next((b for b in self.blobs if b.blob_id == blob1_id), None)
        blob2 = next((b for b in self.blobs if b.blob_id == blob2_id), None)
        
        if not blob1 or not blob2:
            return "Invalid blob IDs provided."
        
        # Create a scenario if none was provided
        if not scenario:
            scenarios = [
                f"Blobs {blob1_id} and {blob2_id} meet in a food-rich area",
                f"Blob {blob1_id} and {blob2_id} have to share limited resources",
                f"A storm forces blobs {blob1_id} and {blob2_id} to take shelter together",
                f"Blobs {blob1_id} and {blob2_id} accidentally bump into each other",
                f"Blobs {blob1_id} and {blob2_id} discover something interesting"
            ]
            scenario = random.choice(scenarios)
        
        # Get current relationship if any
        current_relationship = blob1.relationships.get(blob2_id, 0.0)
        relationship_text = ""
        if current_relationship > 0.5:
            relationship_text = f"Blobs {blob1_id} and {blob2_id} are good friends."
        elif current_relationship > 0:
            relationship_text = f"Blobs {blob1_id} and {blob2_id} are friendly with each other."
        elif current_relationship > -0.5:
            relationship_text = f"Blobs {blob1_id} and {blob2_id} don't know each other well."
        elif current_relationship > -0.5:
            relationship_text = f"Blobs {blob1_id} and {blob2_id} don't really get along."
        else:
            relationship_text = f"Blobs {blob1_id} and {blob2_id} don't like each other at all."
        
        prompt = (
            f"Write a short, cute story about two blobs interacting:\n\n"
            f"Blob-{blob1_id}: {blob1.behavior} (Traits: {', '.join(blob1.traits)})\n"
            f"Blob-{blob2_id}: {blob2.behavior} (Traits: {', '.join(blob2.traits)})\n\n"
            f"{relationship_text}\n\n"
            f"Scenario: {scenario}\n\n"
            f"Write a fun, simple story (400 chars max) about what happens when these two blobs interact."
        )
        
        messages = [
            {"role": "system", "content": "You write cute, fun stories about blob creatures."},
            {"role": "user", "content": prompt}
        ]
        
        story = AIHelper.ask_ai(messages, temperature=0.7)
        
        # Update relationship based on the story
        is_positive = "friend" in story.lower() or "help" in story.lower() or "happy" in story.lower()
        is_negative = "fight" in story.lower() or "angry" in story.lower() or "sad" in story.lower()
        
        relationship_change = 0.1 if is_positive else -0.1 if is_negative else 0.0
        blob1.update_relationship(blob2_id, relationship_change)
        blob2.update_relationship(blob1_id, relationship_change)
        
        # Update world statistics
        if is_positive:
            self.stats["friendly_meetings"] += 1
        elif is_negative:
            self.stats["unfriendly_meetings"] += 1
        else:
            self.stats["neutral_meetings"] += 1
            
        return story
        
    def get_world_stats(self) -> dict:
        """Get statistics about the current state of the blob world"""
        stats = {
            "time": self.current_time,
            "world_conditions": self.world_conditions.copy(),
            "world_stats": self.stats.copy(),
            "blob_count": len(self.blobs),
            "group_count": len(self.groups),
            "event_count": len(self.events),
            "average_blob_stats": {},
            "group_info": []
        }
        
        # Calculate average blob stats
        for stat in ("energy", "health", "social", "learning"):
            values = [b.stats[stat] for b in self.blobs if stat in b.stats]
            stats["average_blob_stats"][stat] = sum(values) / len(values) if values else 0
            
        # Gather group information
        for group in self.groups:
            group_data = {
                "id": group.group_id,
                "name": group.name,
                "member_count": len(group.members),
                "stats": group.stats.copy()
            }
            stats["group_info"].append(group_data)
            
        return stats

if __name__ == "__main__":
    # Example usage
    world = BlobWorld()
    
    # Set up the world with 8 blobs and 3 groups
    print("Setting up the blob world...")
    world.setup_world(8, 3)
    
    # Run first step of the story
    print("\nAdvancing the story (step 1)...")
    event = world.advance_story()
    if event:
        print(f"\nEvent Time={event.time}: {event.name}")
        print(f"Story: {event.description}")
        print("Effects:")
        for blob_id, effect in event.effects.items():
            blob = next((b for b in world.blobs if b.blob_id == blob_id), None)
            name = f"Blob-{blob_id}" if blob else f"Something-{blob_id}"
            print(f"- {name}: {effect}")
    
    # Create a story about two blobs interacting
    print("\nCreating a story about two blobs...")
    if len(world.blobs) >= 2:
        blob1, blob2 = world.blobs[0], world.blobs[1]
        story = world.blob_relationship_story(blob1.blob_id, blob2.blob_id)
        print(f"Story about Blob-{blob1.blob_id} and Blob-{blob2.blob_id}:")
        print(story)
    
    # Make a change to the world
    print("\nMaking a change to the world...")
    result = world.make_change("A big rainstorm comes to the blob world!")
    print(f"Result: {result}")
    
    # Run another step of the story
    print("\nAdvancing the story (step 2)...")
    event = world.advance_story()
    if event:
        print(f"\nEvent Time={event.time}: {event.name}")
        print(f"Story: {event.description}")
    
    # Create a special event: two groups disagree
    disagreement_prompt = (
        "Group-1 and Group-0 disagree about sharing a large pile of food they found. "
        "Blobs from both groups gather around the food, unsure what to do."
    )

    # Process this change
    result = world.make_change(disagreement_prompt, temperature=0.8)
    print(f"Result: {result}")

    # Run another step of the story
    print("\nAdvancing the story (step 3)...")
    event = world.advance_story()
    if event:
        print(f"\nEvent Time={event.time}: {event.name}")
        print(f"Story: {event.description}")

    # Get a world report
    print("\nGetting world report...")
    report = world.get_world_report()
    print(f"Report: {report}")
    
    # Get world statistics
    print("\nGetting world statistics...")
    stats = world.get_world_stats()
    print(f"World time: Time={stats['time']}")
    print(f"Blob count: {stats['blob_count']}")
    print(f"Group count: {stats['group_count']}")
    print(f"World conditions: {', '.join([f'{k}={v:.2f}' for k,v in stats['world_conditions'].items()])}")
    print(f"Average blob stats: {', '.join([f'{k}={v:.2f}' for k,v in stats['average_blob_stats'].items()])}")