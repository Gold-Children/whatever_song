import requests, base64
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Playlist, SpotifyToken
from .serializers import PlaylistSerializer
from WhateverSong.config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, TOKEN_URL


# 토큰 발급
def get_access_token(refresh_token):
    encoded = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8"))
    headers = {
        # 'Authorization': f'Basic {encoded}',
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        # 'refresh_token': REFRESH_TOKEN
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    # print("Status Code:", response.status_code)
    # print("Response Data:", response.json())
    response_data = response.json()
    return response_data.get("access_token")


# playlist 조회
class PlaylistAPIView(APIView):
    def get(self, request):
        access_token = get_access_token(request.user)
        print(access_token)

        if not access_token:
            return Response({"error": "토큰이 유효하지 않습니다."}, status=400)

        headers = {"Authorization": f"Bearer {access_token}"}

        # spotify api 호출
        spotify_api = requests.get(
            "https://api.spotify.com/v1/browse/featured-playlists", headers=headers
        )
        spotify_data = spotify_api.json()
        return Response(spotify_data, status=200)


class PlaylistSearchAPIView(APIView):
    def post(self, request):
        pass
