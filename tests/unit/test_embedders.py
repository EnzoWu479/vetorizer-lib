"""Unit tests for embedders.

Tests for TextEmbedder with mocked model.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestTextEmbedder:
    """Tests for TextEmbedder class."""

    def test_embedder_has_dimension_property(self) -> None:
        """TextEmbedder exposes embedding dimension."""
        from vetorizer_lib.embedders.text import TextEmbedder

        with patch("vetorizer_lib.embedders.text.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model

            embedder = TextEmbedder()
            assert embedder.dimension == 384

    def test_embedder_has_model_name_property(self) -> None:
        """TextEmbedder exposes model name."""
        from vetorizer_lib.embedders.text import TextEmbedder

        with patch("vetorizer_lib.embedders.text.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model

            embedder = TextEmbedder(model_name="test-model")
            assert embedder.model_name == "test-model"

    def test_embed_returns_list_of_vectors(self) -> None:
        """TextEmbedder.embed returns list of float vectors."""
        from vetorizer_lib.embedders.text import TextEmbedder
        import numpy as np

        with patch("vetorizer_lib.embedders.text.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_model.encode.return_value = np.array([[0.1] * 384, [0.2] * 384])
            mock_st.return_value = mock_model

            embedder = TextEmbedder()
            vectors = embedder.embed(["text1", "text2"])

            assert len(vectors) == 2
            assert len(vectors[0]) == 384
            assert isinstance(vectors[0][0], float)

    def test_embed_handles_single_text(self) -> None:
        """TextEmbedder.embed handles single text input."""
        from vetorizer_lib.embedders.text import TextEmbedder
        import numpy as np

        with patch("vetorizer_lib.embedders.text.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_model.encode.return_value = np.array([[0.1] * 384])
            mock_st.return_value = mock_model

            embedder = TextEmbedder()
            vectors = embedder.embed(["single text"])

            assert len(vectors) == 1

    def test_embed_handles_empty_list(self) -> None:
        """TextEmbedder.embed handles empty input list."""
        from vetorizer_lib.embedders.text import TextEmbedder
        import numpy as np

        with patch("vetorizer_lib.embedders.text.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_model.encode.return_value = np.array([]).reshape(0, 384)
            mock_st.return_value = mock_model

            embedder = TextEmbedder()
            vectors = embedder.embed([])

            assert len(vectors) == 0

    def test_default_model_is_minilm(self) -> None:
        """TextEmbedder uses MiniLM as default model."""
        from vetorizer_lib.embedders.text import TextEmbedder

        with patch("vetorizer_lib.embedders.text.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model

            embedder = TextEmbedder()
            
            mock_st.assert_called_once()
            call_args = mock_st.call_args[0][0]
            assert "all-MiniLM-L6-v2" in call_args


class TestTextEmbedderModelConfig:
    """Tests for TextEmbedder model configuration (US3)."""

    def test_custom_model_name_is_used(self) -> None:
        """TextEmbedder uses custom model name when provided."""
        from vetorizer_lib.embedders.text import TextEmbedder

        with patch("vetorizer_lib.embedders.text.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 768
            mock_st.return_value = mock_model

            embedder = TextEmbedder(model_name="sentence-transformers/all-mpnet-base-v2")
            
            mock_st.assert_called_once_with("sentence-transformers/all-mpnet-base-v2")
            assert embedder.model_name == "sentence-transformers/all-mpnet-base-v2"

    def test_invalid_model_raises_model_load_error(self) -> None:
        """TextEmbedder raises ModelLoadError for invalid model."""
        from vetorizer_lib.embedders.text import TextEmbedder
        from vetorizer_lib.exceptions import ModelLoadError

        with patch("vetorizer_lib.embedders.text.SentenceTransformer") as mock_st:
            mock_st.side_effect = Exception("Model not found")

            with pytest.raises(ModelLoadError) as exc_info:
                TextEmbedder(model_name="invalid/nonexistent-model")
            
            assert "invalid/nonexistent-model" in str(exc_info.value)

    def test_dimension_reflects_model(self) -> None:
        """TextEmbedder.dimension reflects the loaded model's dimension."""
        from vetorizer_lib.embedders.text import TextEmbedder

        with patch("vetorizer_lib.embedders.text.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 768
            mock_st.return_value = mock_model

            embedder = TextEmbedder(model_name="custom-model")
            assert embedder.dimension == 768


class TestTextEmbedderSearch:
    """Tests for TextEmbedder query embedding (US2)."""

    def test_embed_query_returns_single_vector(self) -> None:
        """Embedding a single query returns one vector."""
        from vetorizer_lib.embedders.text import TextEmbedder
        import numpy as np

        with patch("vetorizer_lib.embedders.text.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_model.encode.return_value = np.array([[0.1] * 384])
            mock_st.return_value = mock_model

            embedder = TextEmbedder()
            vectors = embedder.embed(["search query"])

            assert len(vectors) == 1
            assert len(vectors[0]) == 384

    def test_embed_query_is_deterministic(self) -> None:
        """Same query produces same embedding."""
        from vetorizer_lib.embedders.text import TextEmbedder
        import numpy as np

        with patch("vetorizer_lib.embedders.text.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            fixed_embedding = np.array([[0.5] * 384])
            mock_model.encode.return_value = fixed_embedding
            mock_st.return_value = mock_model

            embedder = TextEmbedder()
            vec1 = embedder.embed(["test query"])
            vec2 = embedder.embed(["test query"])

            assert vec1 == vec2
