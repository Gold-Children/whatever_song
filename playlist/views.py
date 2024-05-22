import requests, base64
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PlaylistSerializer
from WhateverSong.config import CLIENT_ID, CLIENT_SECRET, TOKEN_URL
from django.shortcuts import get_object_or_404
from .models import Playlist


# 토큰 발급
def get_access_token():
    encoded = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8"))
    headers = {
        # 'Authorization': f'Basic {encoded}',
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    # print("Status Code:", response.status_code)
    # print("Response Data:", response.json())
    response_data = response.json()
    return response_data.get("access_token")


# playlist 조회
class PlaylistAPIView(APIView):
    def get(self, request):
        access_token = get_access_token()

        if not access_token:
            return Response({"error": "토큰이 유효하지 않습니다."}, status=400)

        # spotify api 호출 헤더
        headers = {"Authorization": f"Bearer {access_token}"}

        # spotify api 호출
        spotify_api = requests.get(
            "https://api.spotify.com/v1/browse/featured-playlists", headers=headers
        )
        spotify_data = spotify_api.json()
        return Response(spotify_data, status=200)


# playlist 검색
class PlaylistSearchAPIView(APIView):
    def get(self, request):
        search = request.query_params.get("query", None)

        # 검색어가 없는 경우 오류 응답 반환 - 프론트 구현시 해당 페이지에 머물게 변경
        if not search:
            return Response({"error": "검색어를 입력해주세요."}, status=400)

        access_token = get_access_token()
        if not access_token:
            return Response({"error": "토큰이 유효하지 않습니다."}, status=400)

        # spotify api 호출 헤더, 검색 api에 전달할 파라미터
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"q": search, "type": "playlist"}

        # spotify api 호출
        spotify_api = requests.get(
            "https://api.spotify.com/v1/search", headers=headers, params=params
        )

        spotify_data = spotify_api.json()

        playlists = []
        for item in spotify_data.get("playlists", {}).get("items", []):
            playlist = {
                "name": item["name"],  # 플레이리스트 이름
                "link": item["external_urls"]["spotify"],  # 플레이리스트 링크
                "description": item.get("description", ""),  # 플레이리스트 설명
                "image_url": (
                    item["images"][0]["url"] if item["images"] else None
                ),  # 플레이리스트 이미지 URL (있는 경우)
            }
            # 리스트에 플레이리스트 추가
            playlists.append(playlist)

        return Response(playlists, status=200)


#찜 등록/제거, isauthenticated 없어서 유저 로그인 시스템이랑 결합시 추가해야함
class PlaylistZzimAPIView(APIView):
    def post(self, request, playlist_id):
        playlist = get_object_or_404(Playlist, id=playlist_id)

        if playlist.zzim.filter(id=request.user.id).exists():
            playlist.zzim.remove(request.user)
            message = "찜 목록에서 삭제했습니다."

        else:
            playlist.zzim.add(request.user)
            message = "찜 목록에 추가했습니다."
        
        playlist.save()
        serializer = PlaylistSerializer(playlist)
        return Response({"message": message, "playlist": serializer.data}, status=status.HTTP_200_OK)