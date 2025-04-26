"""
Blob Image Generator Module
--------------------------
This module provides consistent blob image generation based on a reference image.
"""

import base64
import os
import time
from typing import Optional, List

# Import the OpenAI client
import openai

def encode_image(image_path):
    """Encode image to base64 string"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Reference image not found at: {image_path}")
    
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

class BlobImageGenerator:
    """Helper class for consistent blob image generation"""
    
    def __init__(self, api_key: str, reference_image_path: str = "local_blob_example.png"):
        """Initialize with OpenAI API key and reference image path"""
        self.api_key = api_key
        self.reference_image_path = reference_image_path
        self.blob_description = None
        
        # Initialize OpenAI client
        openai.api_key = self.api_key
        
        # Validate reference image exists
        if not os.path.exists(reference_image_path):
            print(f"WARNING: Reference image not found at {reference_image_path}")
        else:
            # Get description of reference blob (only needs to be done once)
            self._analyze_reference_image()
    
    def _analyze_reference_image(self):
        """Analyze the reference image to get detailed description of blob appearance"""
        try:
            # Encode image to base64
            base64_image = encode_image(self.reference_image_path)
            
            # Set up the client
            client = openai.OpenAI(api_key=self.api_key)
            
            # Request description from OpenAI Vision API
            response = client.chat.completions.create(
                model="gpt-4o",  # or "gpt-4o" if available
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe this blob character in detail, focusing on its appearance, shape, colors, facial features, and any unique characteristics. Keep the description under 20 words and focus on visual elements only."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            # Store the description for future use
            self.blob_description = response.choices[0].message.content
            print(f"Reference blob analyzed: {self.blob_description[:100]}...")
            
        except Exception as e:
            print(f"Error analyzing reference image: {str(e)}")
            self.blob_description = "A gelatinous blob creature with simple facial features and a colorful body"
    
    def create_event_image_prompt(self, event_headline: str, event_details: str) -> str:
        """Create a consistent image prompt based on reference blob"""
        
        # Use the analyzed description if available
        blob_style = self.blob_description if self.blob_description else "gelatinous blob creatures with simple expressive faces and colorful bodies"
        
        # Create a detailed prompt that enforces consistency
        prompt = (
            f"Create a single cohesive illustration of an event titled '{event_headline}' "
            f"featuring multiple blob characters with THIS EXACT appearance style: {blob_style}. "
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