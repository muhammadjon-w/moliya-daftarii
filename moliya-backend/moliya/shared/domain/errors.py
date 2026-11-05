"""Domen va ilova qatlamlari ishlatadigan xatolar. HTTP haqida hech narsa bilmaydi."""


class DomainError(Exception):
    code = "domain_error"

    def __init__(self, message: str = "", **details):
        super().__init__(message or self.code)
        self.message = message or self.code
        self.details = details


class ValidationFailed(DomainError):
    code = "validation"


class NotFound(DomainError):
    code = "not_found"


class Forbidden(DomainError):
    code = "forbidden"


class SubscriptionRequired(DomainError):
    """Sinov yoki obuna muddati tugagan: yozish yopiq, o'qish ochiq."""

    code = "subscription"


class ExternalServiceError(DomainError):
    code = "external"
