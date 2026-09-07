from django.urls import path

from apps.shared.views import HomeView

app_name = "shared"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
]
