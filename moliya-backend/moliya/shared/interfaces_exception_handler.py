"""Domen xatolarini HTTP javoblariga aylantiradi. Bitta format: {"error": <kod>, "message": <matn>, ...}."""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_handler

from moliya.shared.domain.errors import (
    DomainError,
    ExternalServiceError,
    Forbidden,
    NotFound,
    SubscriptionRequired,
    ValidationFailed,
)

STATUS = {
    ValidationFailed: status.HTTP_400_BAD_REQUEST,
    NotFound: status.HTTP_404_NOT_FOUND,
    Forbidden: status.HTTP_403_FORBIDDEN,
    SubscriptionRequired: status.HTTP_402_PAYMENT_REQUIRED,
    ExternalServiceError: status.HTTP_502_BAD_GATEWAY,
}


def exception_handler(exc, context):
    if isinstance(exc, DomainError):
        code = next((v for k, v in STATUS.items() if isinstance(exc, k)), status.HTTP_400_BAD_REQUEST)
        return Response({"error": exc.code, "message": exc.message, **exc.details}, status=code)
    response = drf_handler(exc, context)
    if response is not None:
        detail = response.data
        if isinstance(detail, dict) and "detail" in detail:
            response.data = {"error": getattr(exc, "default_code", "error"), "message": str(detail["detail"])}
        elif isinstance(detail, (dict, list)):
            response.data = {"error": "validation", "message": "Ma'lumotlar noto'g'ri.", "fields": detail}
    return response
