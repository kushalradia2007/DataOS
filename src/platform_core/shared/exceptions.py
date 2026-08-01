"""Typed domain exceptions."""

class DomainError(Exception):
    """Base exception for all platform errors."""

class EmptyFileError(DomainError):
    """Raised when an ingested file is empty."""

class UnsupportedFormatError(DomainError):
    """Raised when the file format is unsupported."""
