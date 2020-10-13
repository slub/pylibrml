class ZHSerError(Exception):
    pass


class LibRMLNotValidError(ZHSerError):
    pass


class TemplateNotValidError(ZHSerError):
    pass


class UnknownTemplateError(ZHSerError):
    pass


class OkapiTenantNotFoundError(ZHSerError):
    pass


class OKAPIError(ZHSerError):
    pass


class OkapiModuleNotFoundError(ZHSerError):
    pass


class OkapiDeploymentNotFoundError(ZHSerError):
    pass
