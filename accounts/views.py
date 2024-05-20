from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import CreateAPIView
from django.views.generic import TemplateView
from .serializers import SignupSerializer


class SignUpView(CreateAPIView):
    model = get_user_model()
    serializer_class = SignupSerializer


class SignUpPageView(TemplateView):
    template_name = "accounts/signup.html"


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return JsonResponse(
                {"access": str(refresh.access_token), "refresh": str(refresh)}
            )
        else:
            return JsonResponse(
                {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

    return render(request, "accounts/login.html")


@api_view(["POST"])
def logout(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return JsonResponse(
            {"message": "Successfully logged out"}, status=status.HTTP_200_OK
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)