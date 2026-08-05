import pytest
from common.errors import (
    ZHSerError,
    LibRMLNotValidError,
    TemplateNotValidError,
    UnknownTemplateError,
    OkapiTenantNotFoundError,
    OKAPIError,
    OkapiModuleNotFoundError,
    OkapiDeploymentNotFoundError,
)


def test_custom_errors_hierarchy():
    # Test all custom errors inherit from ZHSerError which inherits from Exception
    errors = [
        LibRMLNotValidError,
        TemplateNotValidError,
        UnknownTemplateError,
        OkapiTenantNotFoundError,
        OKAPIError,
        OkapiModuleNotFoundError,
        OkapiDeploymentNotFoundError,
    ]

    for err_cls in errors:
        assert issubclass(err_cls, ZHSerError)
        assert issubclass(err_cls, Exception)


def test_raising_custom_errors():
    with pytest.raises(LibRMLNotValidError, match="Some librml validation issue"):
        raise LibRMLNotValidError("Some librml validation issue")

    with pytest.raises(TemplateNotValidError, match="Template validation failed"):
        raise TemplateNotValidError("Template validation failed")

    with pytest.raises(UnknownTemplateError, match="Template unknown"):
        raise UnknownTemplateError("Template unknown")
