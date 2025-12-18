"""Unit tests for ImageEmbedder.

Tests for CLIP-based image embedding with mocked model.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestImageEmbedder:
    """Tests for ImageEmbedder class (US4)."""

    def test_embedder_has_dimension_property(self) -> None:
        """ImageEmbedder exposes embedding dimension."""
        from vetorizer_lib.embedders.image import ImageEmbedder

        with patch("vetorizer_lib.embedders.image.CLIPModel") as mock_clip:
            with patch("vetorizer_lib.embedders.image.CLIPProcessor") as mock_proc:
                mock_model = MagicMock()
                mock_model.config.projection_dim = 512
                mock_clip.from_pretrained.return_value = mock_model
                mock_proc.from_pretrained.return_value = MagicMock()

                embedder = ImageEmbedder()
                assert embedder.dimension == 512

    def test_embedder_has_model_name_property(self) -> None:
        """ImageEmbedder exposes model name."""
        from vetorizer_lib.embedders.image import ImageEmbedder

        with patch("vetorizer_lib.embedders.image.CLIPModel") as mock_clip:
            with patch("vetorizer_lib.embedders.image.CLIPProcessor") as mock_proc:
                mock_model = MagicMock()
                mock_model.config.projection_dim = 512
                mock_clip.from_pretrained.return_value = mock_model
                mock_proc.from_pretrained.return_value = MagicMock()

                embedder = ImageEmbedder(model_name="test-clip-model")
                assert embedder.model_name == "test-clip-model"

    def test_default_model_is_clip(self) -> None:
        """ImageEmbedder uses CLIP as default model."""
        from vetorizer_lib.embedders.image import ImageEmbedder

        with patch("vetorizer_lib.embedders.image.CLIPModel") as mock_clip:
            with patch("vetorizer_lib.embedders.image.CLIPProcessor") as mock_proc:
                mock_model = MagicMock()
                mock_model.config.projection_dim = 512
                mock_clip.from_pretrained.return_value = mock_model
                mock_proc.from_pretrained.return_value = MagicMock()

                embedder = ImageEmbedder()
                
                assert "clip" in embedder.model_name.lower()

    def test_embed_text_returns_vectors(self) -> None:
        """ImageEmbedder.embed returns vectors for text."""
        from vetorizer_lib.embedders.image import ImageEmbedder
        import torch

        with patch("vetorizer_lib.embedders.image.CLIPModel") as mock_clip:
            with patch("vetorizer_lib.embedders.image.CLIPProcessor") as mock_proc:
                mock_model = MagicMock()
                mock_model.config.projection_dim = 512
                mock_model.get_text_features.return_value = torch.randn(1, 512)
                mock_clip.from_pretrained.return_value = mock_model
                
                mock_processor = MagicMock()
                mock_processor.return_value = {"input_ids": torch.zeros(1, 10)}
                mock_proc.from_pretrained.return_value = mock_processor

                embedder = ImageEmbedder()
                vectors = embedder.embed(["test text"])

                assert len(vectors) == 1
                assert len(vectors[0]) == 512

    def test_embed_image_returns_vectors(self) -> None:
        """ImageEmbedder.embed_image returns vectors for images."""
        from vetorizer_lib.embedders.image import ImageEmbedder
        import torch

        with patch("vetorizer_lib.embedders.image.CLIPModel") as mock_clip:
            with patch("vetorizer_lib.embedders.image.CLIPProcessor") as mock_proc:
                with patch("vetorizer_lib.embedders.image.Image") as mock_pil:
                    mock_model = MagicMock()
                    mock_model.config.projection_dim = 512
                    mock_model.get_image_features.return_value = torch.randn(1, 512)
                    mock_clip.from_pretrained.return_value = mock_model
                    
                    mock_processor = MagicMock()
                    mock_processor.return_value = {"pixel_values": torch.zeros(1, 3, 224, 224)}
                    mock_proc.from_pretrained.return_value = mock_processor
                    
                    mock_pil.open.return_value = MagicMock()

                    embedder = ImageEmbedder()
                    vectors = embedder.embed_image(["test.jpg"])

                    assert len(vectors) == 1
                    assert len(vectors[0]) == 512

    def test_invalid_model_raises_error(self) -> None:
        """ImageEmbedder raises ModelLoadError for invalid model."""
        from vetorizer_lib.embedders.image import ImageEmbedder
        from vetorizer_lib.exceptions import ModelLoadError

        with patch("vetorizer_lib.embedders.image.CLIPModel") as mock_clip:
            mock_clip.from_pretrained.side_effect = Exception("Model not found")

            with pytest.raises(ModelLoadError):
                ImageEmbedder(model_name="invalid/model")
