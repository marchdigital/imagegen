import os
import httpx
import hashlib
from datetime import datetime
from pathlib import Path

async def save_image_locally(image_url: str, prompt: str) -> str:
    """Download and save image to local storage"""
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in " -_")
    filename = f"{timestamp}_{safe_prompt}.png"
    
    # Ensure storage directory exists
    storage_path = Path("storage/images")
    storage_path.mkdir(parents=True, exist_ok=True)
    
    # Download image
    async with httpx.AsyncClient() as client:
        response = await client.get(image_url)
        
    # Save to file
    file_path = storage_path / filename
    file_path.write_bytes(response.content)
    
    return str(file_path)
