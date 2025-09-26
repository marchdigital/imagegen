# backend/providers/fal_ai.py
import httpx
import asyncio
from typing import Dict, Any, Optional
from backend.providers.base import BaseProvider, GenerationResult
from backend.config import settings
import base64
import io
from PIL import Image


class FalAIProvider(BaseProvider):
    """Fal.ai provider implementation"""
    
    def __init__(self):
        super().__init__()
        self.name = "Fal.ai"
        self.base_url = "https://fal.run"
        self.api_key = settings.FAL_API_KEY
        
        # Model mappings
        self.models = {
            "flux-pro": "fal-ai/flux-pro",
            "flux-dev": "fal-ai/flux/dev",
            "flux-schnell": "fal-ai/flux/schnell",
            "sdxl": "fal-ai/fast-sdxl",
            "sd15": "fal-ai/stable-diffusion-v1-5",
            "lightning-sdxl": "fal-ai/fast-lightning-sdxl",
            "lcm-sdxl": "fal-ai/lcm-sd15",
            "stable-cascade": "fal-ai/stable-cascade",
            "pixart-sigma": "fal-ai/pixart-sigma",
            "aura-flow": "fal-ai/aura-flow"
        }
        
        self.headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        model: str = "flux-dev",
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        cfg_scale: float = 7.5,
        seed: Optional[int] = None,
        sampler: Optional[str] = None,
        **kwargs
    ) -> GenerationResult:
        """Generate image using Fal.ai"""
        
        # Get the correct model endpoint
        model_endpoint = self.models.get(model, model)
        
        # Build request payload based on model
        payload = self._build_payload(
            model_endpoint, prompt, negative_prompt,
            width, height, steps, cfg_scale, seed, sampler, **kwargs
        )
        
        try:
            async with httpx.AsyncClient() as client:
                # Submit generation request
                response = await client.post(
                    f"{self.base_url}/{model_endpoint}",
                    headers=self.headers,
                    json=payload,
                    timeout=120.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"Fal.ai API error: {response.text}")
                
                result = response.json()
                
                # Handle different response formats
                if "images" in result:
                    image_url = result["images"][0]["url"]
                elif "image" in result:
                    image_url = result["image"]["url"]
                else:
                    raise Exception("Unexpected response format from Fal.ai")
                
                # Download the image
                image_data = await self._download_image(client, image_url)
                
                return GenerationResult(
                    success=True,
                    image_data=image_data,
                    metadata={
                        "model": model,
                        "width": width,
                        "height": height,
                        "steps": steps,
                        "cfg_scale": cfg_scale,
                        "seed": result.get("seed", seed),
                        "sampler": sampler,
                        "provider": "fal.ai"
                    },
                    cost=self._calculate_cost(model, width, height)
                )
                
        except asyncio.TimeoutError:
            raise Exception("Generation timed out")
        except Exception as e:
            return GenerationResult(
                success=False,
                error=str(e)
            )
    
    def _build_payload(
        self,
        model: str,
        prompt: str,
        negative_prompt: Optional[str],
        width: int,
        height: int,
        steps: int,
        cfg_scale: float,
        seed: Optional[int],
        sampler: Optional[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Build request payload based on model requirements"""
        
        # Base payload
        payload = {
            "prompt": prompt,
            "image_size": {
                "width": width,
                "height": height
            }
        }
        
        # Add optional parameters based on model
        if "flux" in model:
            # Flux models have different parameters
            if negative_prompt:
                payload["negative_prompt"] = negative_prompt
            if steps:
                payload["num_inference_steps"] = steps
            if cfg_scale:
                payload["guidance_scale"] = cfg_scale
            if seed and seed != -1:
                payload["seed"] = seed
        elif "sdxl" in model or "sd15" in model:
            # Stable Diffusion models
            if negative_prompt:
                payload["negative_prompt"] = negative_prompt
            payload["num_inference_steps"] = steps
            payload["guidance_scale"] = cfg_scale
            if seed and seed != -1:
                payload["seed"] = seed
            if sampler:
                payload["scheduler"] = self._map_sampler(sampler)
            
            # Enable safety checker option
            payload["enable_safety_checker"] = kwargs.get("safety_checker", False)
            
            # Image-to-image parameters
            if kwargs.get("init_image"):
                payload["init_image"] = kwargs["init_image"]
                payload["strength"] = kwargs.get("denoising_strength", 0.75)
        
        # Add any extra model-specific parameters
        if kwargs.get("extra_params"):
            payload.update(kwargs["extra_params"])
        
        return payload
    
    def _map_sampler(self, sampler: str) -> str:
        """Map common sampler names to Fal.ai scheduler names"""
        sampler_map = {
            "DPM++ 2M Karras": "DPMSolverMultistep",
            "Euler a": "EulerAncestralDiscrete",
            "Euler": "EulerDiscrete",
            "DDIM": "DDIM",
            "LMS": "LMSDiscrete",
            "PNDM": "PNDM",
            "DDPM": "DDPM"
        }
        return sampler_map.get(sampler, "DPMSolverMultistep")
    
    async def _download_image(self, client: httpx.AsyncClient, url: str) -> bytes:
        """Download image from URL"""
        response = await client.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to download image: {response.status_code}")
        return response.content
    
    def _calculate_cost(self, model: str, width: int, height: int) -> float:
        """Calculate generation cost based on model and resolution"""
        # Approximate costs per generation (in USD)
        cost_map = {
            "flux-pro": 0.05,
            "flux-dev": 0.03,
            "flux-schnell": 0.01,
            "sdxl": 0.003,
            "sd15": 0.001,
            "lightning-sdxl": 0.002,
            "stable-cascade": 0.004
        }
        
        base_cost = cost_map.get(model, 0.003)
        
        # Adjust for resolution
        pixels = width * height
        base_pixels = 1024 * 1024
        resolution_multiplier = pixels / base_pixels
        
        return base_cost * resolution_multiplier
    
    async def list_models(self) -> list:
        """List available models"""
        return [
            {
                "id": "flux-pro",
                "name": "Flux Pro",
                "description": "Latest Flux model with best quality",
                "max_width": 1920,
                "max_height": 1920,
                "supports_img2img": True,
                "supports_inpainting": False
            },
            {
                "id": "flux-dev",
                "name": "Flux Dev",
                "description": "Development version of Flux",
                "max_width": 1920,
                "max_height": 1920,
                "supports_img2img": True,
                "supports_inpainting": False
            },
            {
                "id": "flux-schnell",
                "name": "Flux Schnell",
                "description": "Fast Flux generation",
                "max_width": 1920,
                "max_height": 1920,
                "supports_img2img": False,
                "supports_inpainting": False
            },
            {
                "id": "sdxl",
                "name": "Stable Diffusion XL",
                "description": "SDXL with fast generation",
                "max_width": 1536,
                "max_height": 1536,
                "supports_img2img": True,
                "supports_inpainting": True
            },
            {
                "id": "sd15",
                "name": "Stable Diffusion 1.5",
                "description": "Classic SD 1.5 model",
                "max_width": 768,
                "max_height": 768,
                "supports_img2img": True,
                "supports_inpainting": True
            },
            {
                "id": "lightning-sdxl",
                "name": "Lightning SDXL",
                "description": "Ultra-fast SDXL variant",
                "max_width": 1024,
                "max_height": 1024,
                "supports_img2img": False,
                "supports_inpainting": False
            }
        ]
    
    async def check_status(self) -> bool:
        """Check if the provider is available"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    timeout=5.0
                )
                return response.status_code == 200
        except:
            return False
    
    async def get_queue_status(self, request_id: str) -> Dict[str, Any]:
        """Get status of a queued request"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/requests/{request_id}/status",
                headers=self.headers
            )
            return response.json()


# backend/providers/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class GenerationResult:
    """Result from image generation"""
    success: bool
    image_data: Optional[bytes] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    cost: float = 0.0


class BaseProvider(ABC):
    """Base class for all AI image generation providers"""
    
    def __init__(self):
        self.name = "BaseProvider"
        self.api_key = None
        self.base_url = None
    
    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        model: str = "default",
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        cfg_scale: float = 7.5,
        seed: Optional[int] = None,
        sampler: Optional[str] = None,
        **kwargs
    ) -> GenerationResult:
        """Generate an image based on the given parameters"""
        pass
    
    @abstractmethod
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models for this provider"""
        pass
    
    @abstractmethod
    async def check_status(self) -> bool:
        """Check if the provider is available and API key is valid"""
        pass
    
    def validate_parameters(self, **params) -> Dict[str, Any]:
        """Validate and adjust parameters for the provider"""
        # Default validation
        validated = {}
        
        # Ensure dimensions are within limits
        validated["width"] = min(max(params.get("width", 512), 64), 2048)
        validated["height"] = min(max(params.get("height", 512), 64), 2048)
        
        # Ensure dimensions are multiples of 8
        validated["width"] = (validated["width"] // 8) * 8
        validated["height"] = (validated["height"] // 8) * 8
        
        # Validate other parameters
        validated["steps"] = min(max(params.get("steps", 20), 1), 150)
        validated["cfg_scale"] = min(max(params.get("cfg_scale", 7.5), 1.0), 30.0)
        
        return validated


# backend/providers/__init__.py
from backend.providers.fal_ai import FalAIProvider
# from backend.providers.replicate_ai import ReplicateProvider
# from backend.providers.openai_provider import OpenAIProvider
# from backend.providers.openrouter import OpenRouterProvider

def initialize_providers():
    """Initialize all configured providers"""
    providers = []
    
    # Initialize Fal.ai if configured
    from backend.config import settings
    if settings.FAL_API_KEY:
        providers.append(FalAIProvider())
    
    # Add other providers...
    
    return providers