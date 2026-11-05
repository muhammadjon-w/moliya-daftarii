from rest_framework.response import Response
from rest_framework.views import APIView

from moliya.accounts.application.use_cases import access_for, serialize_access
from moliya.shared.domain.clock import utcnow


def serialize_account(account) -> dict:
    return {
        "id": account.id,
        "firstName": account.first_name,
        "lastName": account.last_name,
        "username": account.username,
        "languageCode": account.language_code,
    }


class MeView(APIView):
    """GET /api/v1/me — foydalanuvchi va obuna holati."""

    def get(self, request):
        account = request.user.account
        return Response({"account": serialize_account(account), "access": serialize_access(access_for(account, utcnow()))})
