"""Custom exceptions for the Vetorizer library.

All exceptions inherit from VetorizerError for easy catching of library-specific errors.
Each exception includes actionable error messages with cause and suggested resolution.
"""


class VetorizerError(Exception):
    """Base exception for all Vetorizer errors.

    Args:
        message: Human-readable error description.
        cause: Optional underlying cause of the error.

    Example:
        >>> try:
        ...     raise VetorizerError("Something went wrong")
        ... except VetorizerError as e:
        ...     print(e)
        Something went wrong
    """

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.cause = cause

    def __str__(self) -> str:
        if self.cause:
            return f"{self.message} (caused by: {self.cause})"
        return self.message


class ConfigurationError(VetorizerError):
    """Invalid configuration or missing parameters.

    Raised when:
    - Required configuration parameters are missing
    - Configuration values are invalid
    - Incompatible configuration combinations are detected

    Example:
        >>> raise ConfigurationError("content_column 'text' not found in CSV")
    """


class ConnectionError(VetorizerError):
    """Cannot connect to Qdrant vector database.

    Raised when:
    - Qdrant server is unreachable
    - Connection timeout occurs
    - Authentication fails

    Example:
        >>> raise ConnectionError(
        ...     "Cannot connect to Qdrant at http://localhost:6333. "
        ...     "Ensure Qdrant is running or use in-memory mode."
        ... )
    """


class ModelLoadError(VetorizerError):
    """Cannot load the embedding model from HuggingFace.

    Raised when:
    - Model name is invalid or not found
    - Model download fails
    - Model is incompatible with the library

    Example:
        >>> raise ModelLoadError(
        ...     "Cannot load model 'invalid-model'. "
        ...     "Check the model name on HuggingFace Hub."
        ... )
    """


class IngestError(VetorizerError):
    """Error during data ingestion.

    Raised when:
    - CSV file cannot be read
    - Data processing fails
    - Embedding generation fails for a batch

    Example:
        >>> raise IngestError("CSV file 'data.csv' not found")
    """


class SearchError(VetorizerError):
    """Error during search operation.

    Raised when:
    - Query embedding fails
    - Vector database query fails
    - Collection does not exist

    Example:
        >>> raise SearchError("Collection 'products' does not exist")
    """


class VectorCompatibilityError(VetorizerError):
    """Incompatibility between query/ingest mode and stored vector dimensions.

    Example:
        >>> raise VectorCompatibilityError(
        ...     "Database expects hybrid vectors (768), but query produced text vectors (384)."
        ... )
    """
