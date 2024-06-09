from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model, update_session_auth_hash, logout
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.exceptions import MultipleObjectsReturned
from .serializers import SignupSerializer, CustomTokenObtainPairSerializer
from .models import User
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

class SignUpView(CreateAPIView):

    def post(self, request):
        print('request', request)
        data = request.data
        print('data', data)
        print('email3', data['email'])
        print(get_user_model)
        try:
            user = get_user_model().objects.get(email=data['email'])
            print('user', user)

            if user.is_active:
                user.username = data['username']
                user.nickname = data['nickname']
                user.image = data['image']
                user.email = data['email']
                user.set_password(data['password'])
                user.save()
                return Response({'message': '가입되었습니다.'}, status=200)
            else:
                return Response({'error': '이메일 인증이 필요합니다.'}, status=400)

        except ObjectDoesNotExist:
            return Response({'error': '사용자를 찾을 수 없습니다.'}, status=400)

class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        print('1111111111111111111111111111111111111111')
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
        print('token', default_token_generator.check_token(user, token))
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': '인증 완료되었습니다.'}, status=200)
        else:
            return Response({'error': '유효하지 않은 링크입니다.'}, status=status.HTTP_400_BAD_REQUEST)

class SendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):        
        email = request.data.get('email')
        user = None
        try:
            user = get_user_model().objects.get(email=email)
            return Response({'error': '중복된 Email입니다.'}, status=400)
        except get_user_model().DoesNotExist:
            # 사용자가 존재하지 않을 경우 새 사용자 생성
            user = get_user_model().objects.create(
                email=email,
                username=email.split('@')[0],  # 임시로 이메일의 앞부분을 사용자 이름으로 사용
                is_active=False  # 이메일 인증 전까지 비활성화 상태
            )
        self.send_verification_email(user)
        return Response({'message': '이메일 인증 메일이 발송되었습니다.'}, status=200)

    def send_verification_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        subject = '이메일 인증 요청'
        message = render_to_string('accounts/email_verification.html', {
            'user': user,
            'uid': uid,
            'token': token,
            'protocol': 'https',
            'domain': 'whateversong.com'
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

class SignUpPageView(TemplateView):
    template_name = "accounts/signup.html"

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LoginPageView(TemplateView):
    template_name = "accounts/login.html"

class LogoutAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            print(f"Exception: {e}")  # 예외 메시지 출력
        return Response(status=status.HTTP_205_RESET_CONTENT)

def main(request):
    return render(request, "accounts/main.html")

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = SignupSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProfilePageView(TemplateView):
    template_name = "accounts/profile.html"

class ProfileUpdatePageView(TemplateView):
    template_name = "accounts/profile_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_id"] = kwargs.get("pk")
        context["csrf_token"] = self.request.META.get("CSRF_COOKIE")
        return context

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if request.user != user:
            return Response(
                {"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = SignupSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            new_username = serializer.validated_data.get("username")
            if (
                new_username
                and User.objects.exclude(pk=user.pk)
                .filter(username=new_username)
                .exists()
            ):
                return Response(
                    {"error": "이미 존재하는 이름입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            new_nickname = serializer.validated_data.get("nickname")
            if (
                new_nickname
                and User.objects.exclude(pk=user.pk)
                .filter(nickname=new_nickname)
                .exists()
            ):
                return Response(
                    {"error": "이미 존재하는 닉네임입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            new_email = serializer.validated_data.get("email")
            if (
                new_email
                and User.objects.exclude(pk=user.pk).filter(email=new_email).exists()
            ):
                return Response(
                    {"error": "이미 사용중인 이메일입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save()

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "프로필 수정 및 토큰 재발급이 완료되었습니다.",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileImageView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if request.user != user:
            return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SignupSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            with transaction.atomic():
                image_file = request.data.get("image")
                if image_file:
                    user.image.delete()
                    user.image.save(image_file.name, image_file, save=True)
                    serializer.validated_data["image"] = user.image

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if request.user != user:
            return Response({"error": "권한이 없음."}, status=status.HTTP_403_FORBIDDEN)

        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not user.check_password(current_password):
            return Response(
                {"error": "현재 비밀번호가 올바르지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if current_password == new_password:
            return Response(
                {"error": "이전 비밀번호와 같은 비밀번호로 설정할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save()

        update_session_auth_hash(request, user)

        return Response(
            {"message": "비밀번호가 성공적으로 변경되었습니다."},
            status=status.HTTP_200_OK,
        )

class ProfiledeleteView(APIView):
    permission_classes = [IsAuthenticated]

    # 회원 탈퇴
    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        if request.user != user:
            return Response(
                {"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN
            )

        logout(request._request)
        user.delete()

        return Response(
            {"message": "회원 탈퇴 성공하셨습니다"}, status=status.HTTP_204_NO_CONTENT
        )
