"""
Blob Image Generator Module
--------------------------
This module provides consistent blob image generation based on a reference image.
"""

import time
from typing import Optional, List

# Import the OpenAI client
import openai


class BlobImageGenerator:
    """Helper class for consistent blob image generation"""
    
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key and reference image path"""
        self.api_key = api_key
        
        # Initialize OpenAI client
        openai.api_key = self.api_key
        
    def create_event_image_prompt(self, event_headline: str, event_details: str) -> str:
        """Create a consistent image prompt based on reference blob"""
        
        # Use the analyzed description if available
        blob_style = "Green blob, dome-shaped, two black oval eyes, simple and cartoonish appearance"
        
        # Create a detailed prompt that enforces consistency
        prompt = (
            f"Create a single cohesive illustration of an event titled '{event_headline}' "
            f"featuring multiple blob characters with THIS EXACT appearance style: {blob_style}. "
            f"Do not add any other characters that are not blobs. Do not add humans or humanlike entities. Do not add clothes"
            f"The scene depicts: {event_details}. "
            f"Ensure all blobs in the image look like variations of the described blob style, "
            f"maintaining consistent proportions, texture, and design language, just with different "
            f"colors and expressions to show different characters. "
            f"Scene should be bright and whimsical with a fantasy world setting. "
            f"Focus on showing the emotion and action of the event. "
            f"No text, no comic panels, just one clean scene with vibrant colors."
        )
        
        # Ensure prompt isn't too long
        if len(prompt) > 900:
            prompt = prompt[:897] + "..."
            
        return prompt
    
    def generate_image(self, prompt: str, n: int = 1, size: str = "1024x1024", 
                      max_retries: int = 3, retry_delay: int = 2) -> List[str]:
        """Generate image using OpenAI API with consistent blob style"""
        
        # Ensure prompt isn't too long for the API
        if len(prompt) > 1000:
            prompt = prompt[:997] + "..."
        
        # Try to create client with API key
        client = openai.OpenAI(api_key=self.api_key)
        
        attempt = 0
        while attempt < max_retries:
            try:
                # Generate the image
                resp = client.images.generate(
                    model="dall-e-3",  # Using the most advanced model
                    prompt=prompt,
                    n=n,
                    size=size,
                    #quality="hd",  # Higher quality images
                    style="vivid"  # More colorful and vibrant
                )
                return [img.url for img in resp.data]
                
            except Exception as e:
                attempt += 1
                if attempt >= max_retries:
                    print(f"Failed to generate image after {max_retries} attempts: {str(e)}")
                    return []
                print(f"Image API error: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
        
        return []