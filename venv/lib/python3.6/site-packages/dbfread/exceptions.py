class DBFNotFound(IOError):
    """Raised if the DBF file was not found."""
    pass

class MissingMemoFile(IOError):
    """Raised if the corresponding memo file was not found."""

__all__ = ['DBFNotFound', 'MissingMemoFile']

