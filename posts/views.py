from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Post, Comment
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .serializers import PostSerializer, CommentSerializer
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Count

class PostAPIView(APIView):

    def get(self, request):
        category = request.GET.get('category')
        sort = request.GET.get('sort', '-created_at')
        posts = Post.objects.all()

        if category:
            posts = posts.filter(category=category)

        posts = posts.annotate(likes_count=Count('like'))

        if sort == "-like":
            posts = posts.order_by('-likes_count', '-created_at')
        else:
            posts = posts.order_by(sort)

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        print(request.data)
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
        data = serializer.data
        print('commentid', post.comments)
        like = False
        if request.user.id in data['like']:
            like = True
        data = {'data':data, 'like':like}
        return Response(data, status=status.HTTP_200_OK)

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
        print("request.data: ", request.data)
        serializer = CommentSerializer(data=request.data)
        print("serializer: ", serializer)
        if serializer.is_valid(raise_exception=True):
            serializer.save(post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostDetailView(TemplateView):
    template_name = "posts/detail.html"

class PostUpdateView(TemplateView):
    template_name = "posts/update.html"


class CommentAPIView(APIView):

    def get_object(self, comment_id):
        return get_object_or_404(Comment, pk=comment_id)

    def put(self, request, comment_id):
        comment = self.get_object(comment_id)
        serializer = CommentSerializer(
            comment, data=request.data, partial=True) 
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    
    def delete(self, request, comment_id):
        comment = self.get_object(comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class LikeAPIView(APIView):
    def get_object(self, postID):
        return get_object_or_404(Post, pk=postID)
    
    def post(self, request, postID):
        post = self.get_object(postID)
        if post.like.filter(pk=request.user.pk).exists():
            post.like.remove(request.user)
        else:
            post.like.add(request.user)
        return Response(status=status.HTTP_200_OK)