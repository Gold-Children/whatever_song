from rest_framework import serializers
from .models import Playlist


class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'


    # 사용자 찜여부 반환
    def get_zzim(self, obj):
        user = self.context['request'].user
        return obj.zzim.filter(id=user.id).exists()