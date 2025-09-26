from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseProvider(ABC):
    """Base class for all AI providers"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @abstractmethod
    async def generate(self, **kwargs) -> Dict[str, Any]:
        """Generate an image"""
        pass
    
    @abstractmethod
    async def get_models(self) -> list:
        """Get available models"""
        pass
    
    async def generate_wan25(self, **kwargs) -> Dict[str, Any]:
        """Generate using WAN-25 model - default implementation"""
        return await self.generate(**kwargs)
    
    async def edit_qwen(self, **kwargs) -> Dict[str, Any]:
        """Edit using Qwen model - default implementation"""
        raise NotImplementedError("Qwen editing not implemented for this provider")
    
    async def generate_product_shoot(self, **kwargs) -> Dict[str, Any]:
        """Generate product photography - default implementation"""
        raise NotImplementedError("Product shoot not implemented for this provider")
