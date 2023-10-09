from rest_framework import serializers
from .models import UserProfile,Categories,PostComment,Post
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['id', 'name']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'image', 'firstName', 'lastName', 'email']

class PostCommentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only = True)
    class Meta:
        model = PostComment
        user = UserProfileSerializer(read_only = True)
        fields = ['id', 'createdAt', 'comment', 'user']

class PostSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer(read_only = True)
    category = CategoriesSerializer(read_only = True)
    isLiked = serializers.SerializerMethodField()
    post_comment = PostCommentSerializer(read_only = True,many=True)
    likeCount = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields=['id','createdAt','category','isLiked','likeCount','post_comment','image','text','title','html','author','slug','updatedAt']
        

    def get_isLiked(self, obj):
        request = self.context.get('request')
        userId = request.userId
        if not userId:
            return False
        user = User.objects.get(id = userId)
        profile  = get_object_or_404(UserProfile,user = user)
        return profile in obj.like.all()
    
    def get_likeCount(self,obj):
        return obj.like.all().count()