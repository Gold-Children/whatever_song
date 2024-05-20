from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import SignupSerializer
from .models import User
# Create your views here.
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = SignupSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)