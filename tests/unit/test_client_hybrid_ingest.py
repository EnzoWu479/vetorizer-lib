from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from tests.unit.test_mocks_embedders import FakeImageEmbedder, FakeTextEmbedder
from vetorizer_lib.client import VetorizerClient
from vetorizer_lib.models.document import ContentType, Document


def test_ingest_hybrid_csv_embeds_text_and_image_and_concatenates(monkeypatch: pytest.MonkeyPatch) -> None:
    client = VetorizerClient(model_name="dummy")

    client._embedder = FakeTextEmbedder(dimension=3)  # noqa: SLF001
    client._image_embedder = FakeImageEmbedder(dimension=2)  # noqa: SLF001

    store = MagicMock()
    client._store = store  # noqa: SLF001

    def fake_read_csv_batches(*_args, **_kwargs):
        yield [
            Document(
                id="1",
                content="hello",
                content_type=ContentType.TEXT,
                metadata={"image_path": "img.png"},
            )
        ]

    monkeypatch.setattr("vetorizer_lib.ingest.csv.read_csv_batches", fake_read_csv_batches)

    # Contract: this method will be introduced in US1 implementation.
    result = client.ingest_hybrid_csv(
        file_path="data.csv",
        text_column="text",
        image_column="image_path",
        metadata_columns=[],
    )

    assert result.processed == 1
    assert store.upsert.call_count == 1

    upserted_docs = store.upsert.call_args.args[0]
    assert len(upserted_docs) == 1

    doc = upserted_docs[0]
    # With per-modality normalization:
    # Text [0.1, 0.1, 0.1] normalized → [0.577..., 0.577..., 0.577...]
    # Image [0.3, 0.3] normalized → [0.707..., 0.707...]
    embedding = doc.embedding
    assert len(embedding) == 5  # 3 text + 2 image dimensions
    # Check text part is normalized (all equal values)
    assert abs(embedding[0] - 0.577) < 0.01
    assert abs(embedding[1] - 0.577) < 0.01
    assert abs(embedding[2] - 0.577) < 0.01
    # Check image part is normalized (all equal values)
    assert abs(embedding[3] - 0.707) < 0.01
    assert abs(embedding[4] - 0.707) < 0.01
    assert doc.modalities == ["text", "image"]
    assert doc.composition_metadata == {"hybrid_order": ["text", "image"]}
