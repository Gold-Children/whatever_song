from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from django.db import transaction
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

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, username):
        user = get_object_or_404(User, username=username)

        if request.user != user:
            return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SignupSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            # 사용자명(ID)
            new_username = serializer.validated_data.get('username')
            if new_username and User.objects.exclude(pk=user.pk).filter(username=new_username).exists():
                return Response({"error": "이미 존재하는 사용자명입니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            # 닉네임
            new_nickname = serializer.validated_data.get('nickname')
            if new_nickname and User.objects.exclude(pk=user.pk).filter(nickname=new_nickname).exists():
                return Response({"error": "이미 존재하는 닉네임입니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            # 이메일 중복 확인
            new_email = serializer.validated_data.get('email')
            if new_email and User.objects.exclude(pk=user.pk).filter(email=new_email).exists():
                return Response({"error": "이미 사용중인 이메일입니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
class ProfileImageView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, username):
        user = get_object_or_404(User, username=username)

        
        if request.user != user:
            return Response({"error": "권한 읍서요"}, status=status.HTTP_403_FORBIDDEN)

        serializer = SignupSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            with transaction.atomic():
                image_file = request.data.get('image')
                if image_file:
                    # 기존 이미지 삭제
                    user.image.delete()  
                    user.image.save(image_file.name, image_file, save=True)
                    serializer.validated_data['image'] = user.image

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
