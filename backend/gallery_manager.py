from pathlib import Path
import json
import shutil
from datetime import datetime
from typing import List, Dict
from PIL import Image
import io
import httpx

class GalleryManager:
    def __init__(self):
        self.storage_path = Path("storage/images")
        self.metadata_path = Path("storage/metadata.json")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.load_metadata()
    
    def load_metadata(self):
        """Load image metadata from JSON file"""
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {"images": []}
    
    def save_metadata(self):
        """Save metadata to JSON file"""
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    async def save_image(self, image_url: str, prompt: str, model: str, params: dict) -> dict:
        """Download and save image with metadata"""
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"img_{timestamp}_{len(self.metadata['images'])}.png"
        filepath = self.storage_path / filename
        
        # Download image
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            image_data = response.content
        
        # Save full size
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        # Create thumbnail
        thumb_path = self.storage_path / f"thumb_{filename}"
        img = Image.open(io.BytesIO(image_data))
        img.thumbnail((256, 256), Image.Resampling.LANCZOS)
        img.save(thumb_path)
        
        # Save metadata
        image_info = {
            "id": len(self.metadata['images']) + 1,
            "filename": filename,
            "thumbnail": f"thumb_{filename}",
            "prompt": prompt,
            "model": model,
            "params": params,
            "created_at": datetime.now().isoformat(),
            "tags": [],
            "favorite": False
        }
        
        self.metadata['images'].insert(0, image_info)
        self.save_metadata()
        
        return image_info
    
    def get_gallery(self, limit: int = 50, filter_by: str = None) -> List[Dict]:
        """Get gallery images with optional filtering"""
        images = self.metadata.get('images', [])
        
        if filter_by == 'favorites':
            images = [img for img in images if img.get('favorite')]
        
        return images[:limit]
    
    def toggle_favorite(self, image_id: int) -> bool:
        """Toggle favorite status of an image"""
        for img in self.metadata['images']:
            if img['id'] == image_id:
                img['favorite'] = not img['favorite']
                self.save_metadata()
                return img['favorite']
        return False
