from __future__ import annotations


class FakeTextEmbedder:
    def __init__(self, *, dimension: int = 3) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return [[0.1] * self._dimension for _ in texts]


class FakeImageEmbedder:
    def __init__(self, *, dimension: int = 5) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return [[0.2] * self._dimension for _ in texts]

    def embed_image(self, image_paths: list[str]) -> list[list[float]]:
        if not image_paths:
            return []
        return [[0.3] * self._dimension for _ in image_paths]
