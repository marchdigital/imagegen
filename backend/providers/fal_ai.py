import os
import httpx
import asyncio
from typing import Dict, Any, Optional
import base64
from dotenv import load_dotenv

load_dotenv()

class FalAIProvider:
    def __init__(self):
        self.api_key = os.getenv("FAL_API_KEY")
        self.base_url = "https://fal.run"
        
    async def generate_image(self, prompt: str, model: str = "fal-ai/flux/dev", **kwargs) -> Dict[str, Any]:
        """Generate image using Fal.ai"""
        
        if not self.api_key:
            return {"error": "FAL_API_KEY not set in .env file"}
            
        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Build request
        payload = {
            "prompt": prompt,
            "image_size": {
                "width": kwargs.get("width", 1024),
                "height": kwargs.get("height", 1024)
            },
            "num_inference_steps": kwargs.get("steps", 20),
            "guidance_scale": kwargs.get("cfg_scale", 7.5)
        }
        
        if kwargs.get("negative_prompt"):
            payload["negative_prompt"] = kwargs["negative_prompt"]
            
        if kwargs.get("seed") and kwargs["seed"] != -1:
            payload["seed"] = kwargs["seed"]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{model}",
                    headers=headers,
                    json=payload,
                    timeout=120.0
                )
                
                if response.status_code != 200:
                    return {"error": f"Fal.ai API error: {response.text}"}
                
                result = response.json()
                
                # Get image URL from response
                if "images" in result:
                    image_url = result["images"][0]["url"]
                elif "image" in result:
                    image_url = result["image"]["url"]
                else:
                    return {"error": "Unexpected response format"}
                
                return {
                    "success": True,
                    "image_url": image_url,
                    "seed": result.get("seed"),
                    "model": model
                }
                
        except Exception as e:
            return {"error": str(e)}

# Global instance
fal_provider = FalAIProvider()
