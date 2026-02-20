class MetadataServiceError(Exception):
    """Base error for metadata service."""


class InvalidURL(MetadataServiceError):
    """Raised when the URL input is invalid."""


class CollectionError(MetadataServiceError):
    """Raised when metadata could not be collected."""
