from django.shortcuts import render
from .models import Post, Comment
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .serializers import PostSerializer, CommentSerializer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Count

class PostAPIView(APIView):

    def get(self, request):
        sort = request.GET.get('sort', '-created_at')
        posts = Post.objects.annotate(likes_count=Count('like'))

        if sort == "-like": #좋아요순을 선택하면
            posts = posts.order_by('-likes_count', '-created_at')
        else:
            posts = posts.order_by(sort) #그냥 최신순 
        
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class PostlistView(TemplateView):
    template_name = "posts/list.html"

class PostcreateView(TemplateView):
    template_name = "posts/create.html"

class PostDetailAPIView(APIView):
    
    def get_object(self, post_id):
        return get_object_or_404(Post, pk=post_id)
    
    def get(self, request, post_id):
        post = self.get_object(post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, post_id):
        post = self.get_object(post_id)
        serializer = PostSerializer(
            post, data=request.data, partial=True) 
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    
    def delete(self, request, post_id):
        post = self.get_object(post_id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #댓글 작성
    def post(self, request, post_id):
        post = self.get_object(post_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostDetailView(TemplateView):
    template_name = "posts/detail.html"

class PostUpdateView(TemplateView):
    template_name = "posts/update.html"