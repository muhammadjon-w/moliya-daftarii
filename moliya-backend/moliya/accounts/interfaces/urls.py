from django.urls import path

from moliya.accounts.interfaces.views import MeView

urlpatterns = [path("me", MeView.as_view(), name="me")]
