import pytest
from model.exceptions import (
    LibRMLError,
    LibRMLNotValidError,
    TemplateNotValidError,
)


def test_custom_errors_hierarchy():
    # Test all custom errors inherit from LibRMLError which inherits from Exception
    errors = [
        LibRMLNotValidError,
        TemplateNotValidError,
    ]

    for err_cls in errors:
        assert issubclass(err_cls, LibRMLError)
        assert issubclass(err_cls, Exception)


def test_raising_custom_errors():
    with pytest.raises(LibRMLNotValidError, match="Some librml validation issue"):
        raise LibRMLNotValidError("Some librml validation issue")

    with pytest.raises(TemplateNotValidError, match="Template validation failed"):
        raise TemplateNotValidError("Template validation failed")
