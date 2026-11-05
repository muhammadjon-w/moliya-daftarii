from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health),
    path("api/v1/", include("moliya.accounts.interfaces.urls")),
    path("api/v1/", include("moliya.ledger.interfaces.urls")),
    path("api/v1/", include("moliya.billing.interfaces.urls")),
    path("api/v1/", include("moliya.notifications.interfaces.urls")),
]
