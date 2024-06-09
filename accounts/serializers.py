from typing import Any, Dict
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = get_user_model()
        fields = ["username", "password", "email", "nickname", "image"]

    def create(self, validated_data):
        user = get_user_model()(
            username=validated_data["username"],
            email=validated_data["email"],
            nickname=validated_data["nickname"],
            image=validated_data.get("image", 'accounts/profile_pics/logo.png/'),
        )
        user.set_password(validated_data["password"])
        user.save()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user_id"] = user.id
        token["user_nickname"] = user.nickname
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user_id"] = self.user.id
        data["user_nickname"] = self.user.nickname
        return data
