from rest_framework import serializers
from accounts.models import User
from .models import Post, Comment

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content', 'created_at', 'updated_at', 'user']
        read_only_fields = ['post']

class PostSerializer(serializers.ModelSerializer):
    #게시글에서 댓글 보이게 수정
    comments = CommentSerializer(many = True, read_only = True)
    author = serializers.PrimaryKeyRelatedField(queryset = User.objects.all())
    author_nickname = serializers.CharField(source='author.nickname')
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['author', 'author_nickname', 'like', 'created_at', 'updated_at']
