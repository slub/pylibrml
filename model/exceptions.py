class LibRMLError(Exception):
    """Base exception class for the pylibrml package."""
    pass


class LibRMLNotValidError(LibRMLError):
    """Raised when a LibRML document or object is not valid."""
    pass


class TemplateNotValidError(LibRMLError):
    """Raised when a template is not valid or meta sidecar is missing."""
    pass
