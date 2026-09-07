from typing import Any

from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView

from apps.authentication.services.helix_login import HelixLoginService
from apps.shared.exceptions import PermissionDeniedError, ValidationError


class LoginPageView(TemplateView):
    template_name = "authentication/login.html"
    redirect_authenticated_user = True


class HelixLoginView(View):
    service = HelixLoginService()

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self.service.build_authorize_redirect(request)


class HelixCallbackView(View):
    service = HelixLoginService()

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        try:
            profile = self.service.complete_login(request)
        except ValidationError:
            messages.error(request, "Login with Helix failed. Please try again.")
            return redirect("authentication:login")
        except PermissionDeniedError:
            return render(request, "authentication/helix_forbidden.html", status=403)
        login(request, profile)
        return redirect("/")


class LogoutView(View):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        logout(request)
        return redirect("authentication:login")


class SignUpView(View):
    template_name = "authentication/signup.html"
    service = UserProfileService()

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return render(request, self.template_name, {"serializer": SignUpSerializer()})

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        serializer = SignUpSerializer(data=request.POST)
        if not serializer.is_valid():
            return render(request, self.template_name, {"serializer": serializer}, status=422)
        try:
            profile = self.service.create(**serializer.validated_data)
        except ValidationError as exc:
            serializer.errors.update(exc.errors)
            return render(request, self.template_name, {"serializer": serializer}, status=422)
        login(request, profile)
        return redirect("shared:home")


class UserProfileSearchView(SearchEndpointView):
    filterset_class = UserProfileFilterSet
    result_template_name = "authentication/partials/user_profile_options.html"
    service = UserProfileService()

    def get_queryset(self) -> QuerySet[UserProfile]:
        return self.service.filter()


class SearchableSelectDemoView(TemplateView):
    template_name = "authentication/demo/searchable_select_demo.html"
