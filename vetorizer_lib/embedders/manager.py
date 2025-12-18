"""Embedder model manager with lazy loading and singleton pattern.

This module manages text and image embedding models with:
- Lazy loading (models loaded on first use)
- Singleton pattern (one instance per model)
- FP16 optimization on GPU
- Thread-safe access
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from sentence_transformers import SentenceTransformer
from transformers import CLIPModel, CLIPProcessor
import torch

if TYPE_CHECKING:
    from PIL import Image


class EmbedderManager:
    """Singleton manager for embedding models.
    
    Manages lazy loading and caching of text and image embedders.
    Thread-safe for concurrent requests.
    
    Attributes:
        _text_model: Cached text embedding model.
        _image_model: Cached image embedding model (CLIP).
        _image_processor: Cached CLIP processor for image preprocessing.
        _lock: Thread lock for safe initialization.
        _device: Torch device (cuda/cpu).
        _use_fp16: Whether to use FP16 precision on GPU.
    """
    
    _instance: EmbedderManager | None = None
    _lock = threading.Lock()
    
    def __new__(cls) -> EmbedderManager:
        """Singleton pattern - ensure only one instance exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize manager (only once due to singleton)."""
        if self._initialized:
            return
        
        self._text_model: SentenceTransformer | None = None
        self._image_model: CLIPModel | None = None
        self._image_processor: CLIPProcessor | None = None
        
        # Determine device and precision
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._use_fp16 = torch.cuda.is_available()
        
        self._model_lock = threading.Lock()
        self._initialized = True
    
    def get_text_embedder(
        self, 
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ) -> SentenceTransformer:
        """Get or load text embedding model.
        
        Args:
            model_name: HuggingFace model identifier.
            
        Returns:
            Loaded SentenceTransformer model.
        """
        with self._model_lock:
            if self._text_model is None:
                self._text_model = SentenceTransformer(model_name, device=str(self._device))
                
                # Enable FP16 on GPU
                if self._use_fp16:
                    self._text_model = self._text_model.half()
        
        return self._text_model
    
    def get_image_embedder(
        self,
        model_name: str = "openai/clip-vit-base-patch16"
    ) -> tuple[CLIPModel, CLIPProcessor]:
        """Get or load image embedding model (CLIP).
        
        Args:
            model_name: HuggingFace CLIP model identifier.
            
        Returns:
            Tuple of (CLIPModel, CLIPProcessor).
        """
        with self._model_lock:
            if self._image_model is None or self._image_processor is None:
                self._image_model = CLIPModel.from_pretrained(model_name).to(self._device)
                self._image_processor = CLIPProcessor.from_pretrained(model_name)
                
                # Enable FP16 on GPU
                if self._use_fp16:
                    self._image_model = self._image_model.half()
                
                # Set to eval mode
                self._image_model.eval()
        
        return self._image_model, self._image_processor
    
    def embed_text(self, text: str, model_name: str | None = None) -> list[float]:
        """Generate text embedding.
        
        Args:
            text: Text to embed.
            model_name: Optional model override.
            
        Returns:
            Text embedding vector.
        """
        model = self.get_text_embedder(model_name or "sentence-transformers/all-MiniLM-L6-v2")
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_image(self, image: Image.Image, model_name: str | None = None) -> list[float]:
        """Generate image embedding using CLIP.
        
        Args:
            image: PIL Image to embed.
            model_name: Optional model override.
            
        Returns:
            Image embedding vector.
        """
        model, processor = self.get_image_embedder(model_name or "openai/clip-vit-base-patch16")
        
        # Process image
        inputs = processor(images=image, return_tensors="pt").to(self._device)
        
        # Convert to FP16 if enabled
        if self._use_fp16:
            inputs = {k: v.half() if v.dtype == torch.float32 else v for k, v in inputs.items()}
        
        # Generate embedding
        with torch.no_grad():
            outputs = model.get_image_features(**inputs)
            # Normalize (CLIP outputs are typically normalized, but ensure it)
            embedding = outputs / outputs.norm(dim=-1, keepdim=True)
        
        return embedding.cpu().numpy().flatten().tolist()
    
    def get_text_dimension(self, model_name: str | None = None) -> int:
        """Get text embedding dimension.
        
        Args:
            model_name: Optional model override.
            
        Returns:
            Embedding dimension.
        """
        model = self.get_text_embedder(model_name or "sentence-transformers/all-MiniLM-L6-v2")
        return model.get_sentence_embedding_dimension()
    
    def get_image_dimension(self, model_name: str | None = None) -> int:
        """Get image embedding dimension.
        
        Args:
            model_name: Optional model override.
            
        Returns:
            Embedding dimension.
        """
        model, _ = self.get_image_embedder(model_name or "openai/clip-vit-base-patch16")
        return model.config.projection_dim


# Global singleton instance
embedder_manager = EmbedderManager()
