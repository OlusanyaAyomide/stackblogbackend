import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from .constants import JWT_SECRET
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Categories,Post,PostComment,UserProfile
from .serializers import UserProfileSerializer,PostSerializer
from django.utils.decorators import method_decorator

class Create_LogIn(APIView):
    def post(self,request,**kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        if not (username and password):
            return Response({'detail': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        AppUser = get_user_model()
        user = User.objects.filter(username = username).exists()
        profile = ""
        if user:    
            user = authenticate(username=username, password=password)
            if user is None:
                return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                profile = get_object_or_404(UserProfile,user=user)
        else:
            image = request.data.get('image')
            firstName = request.data.get('firstName')
            lastName = request.data.get('lastName')
            if not (image and firstName and lastName):
                return Response({'detail': 'Required feids are missing'}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.create(username=username, email=username)
            user.set_password(password)
            user.save()
            profile = UserProfile.objects.create(
                image = image,firstName = firstName ,
                lastName = lastName,email = username,user = user
            )
            
        # expiration_time = datetime.now() + timedelta(days=30)
        serializer = UserProfileSerializer(profile)
        payload = {
            'id': user.id,
            'username': user.username,
            # 'exp': expiration_time
            
        }
        token = jwt.encode(payload,JWT_SECRET, algorithm='HS256')
        return Response({'token': token,"user":serializer.data}, status=status.HTTP_200_OK)
    
class GetProfile(APIView):
    def get(self,request,**kwargs):
        if request.userId is None:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        user = User.objects.get(id=request.userId)
        profile = UserProfile.objects.get(user = user)
        profilesearilzer = UserProfileSerializer(profile)
        profile = profilesearilzer.data
        return Response(profile, status=status.HTTP_200_OK)




class CreateNewBlog(APIView):
    def post(self,request,**kwargs):
        if request.userId is None:
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        
        selected_category =  request.data.get('selected_category')
        user = User.objects.get(id=request.userId)
        author = UserProfile.objects.get(user = user)
        image = request.data.get('image')
        text = request.data.get('text')
        title = request.data.get('title')
        html = request.data.get('html')
        
        if not (selected_category and author and image and text and title and html):
            return Response({'detail': 'Required feids are missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        category  = get_object_or_404(Categories,name=selected_category)
        
        newpost = Post.objects.create(
            author=author,category = category,image=image,
            text=text,title = title,html = html
        )
        serializer = PostSerializer(newpost,context={'request': request})
        return Response({"blog":serializer.data}, status=status.HTTP_200_OK)

    
class GetAllPosts(APIView):
    def get(self,request,**kwargs):
        profile=False
        if request.userId:
            user = get_object_or_404(User,id=request.userId)
            data = get_object_or_404(UserProfile,user = user)
            profilesearilzer = UserProfileSerializer(data)
            profile = profilesearilzer.data
            
        blogs = Post.objects.all().order_by('-createdAt')
        serializer = PostSerializer(blogs,context={'request': request},many=True)
        return Response({"blog":serializer.data,"profile":profile}, status=status.HTTP_200_OK)


class LikePost(APIView):
    def post(self,request,**kwargs):
        if request.userId is None:
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        user = get_object_or_404(User,id=request.userId)
        profile = get_object_or_404(UserProfile,user = user)
        
        slug = request.data.get('slug')
        if not slug:
            return Response({'detail': 'Required feids are missing'}, status=status.HTTP_400_BAD_REQUEST)
          
        post = get_object_or_404(Post,slug=slug)
        if profile in post.like.all():
            post.like.remove(profile)
        else:
            post.like.add(profile)
        post.save()
        
        newpost = get_object_or_404(Post,slug = slug)
        serializer = PostSerializer(newpost,context={'request': request})
        return Response({"blog":serializer.data}, status=status.HTTP_200_OK)


        
class CommentOnPost(APIView):
    def post(self,request,**kwargs):
        if request.userId is None:
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        slug = request.data.get('slug')
        comment = request.data.get('comment')

        if not (slug and comment):
            return Response({'detail': 'Required feids are missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        post = get_object_or_404(Post,slug=slug)
        user = get_object_or_404(User,id=request.userId)
        profile = get_object_or_404(UserProfile,user = user)
        PostComment.objects.create(post=post,user=profile,comment = comment)
        newpost = get_object_or_404(Post,slug = slug)
        serializer = PostSerializer(newpost,context={'request': request})
        return Response({"blog":serializer.data}, status=status.HTTP_200_OK)

class BlogDetail(APIView):
    def get(self,request,**kwargs):
        slug = kwargs['slug']
        post = get_object_or_404(Post,slug=slug)
        serializer = PostSerializer(post,context={'request': request})
        related_post = Post.objects.filter(category = post.category).exclude(id=post.id)[:6]
        related_serializer = PostSerializer(related_post,context={'request': request},many=True)
        return Response({"blog":serializer.data,"related":related_serializer.data}, status=status.HTTP_200_OK)

class EditBlog(APIView):
    def post(self,request,**kwargs):
        slug = request.data.get('slug') 
        user = User.objects.get(id=request.userId)
        author = UserProfile.objects.get(user = user)
        image = request.data.get('image')
        text = request.data.get('text')
        title = request.data.get('title')
        html = request.data.get('html')
        selected_category =  request.data.get('selected_category')
        if not (selected_category and author and image and text and title and html):
            return Response({'detail': 'Required feids are missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        blogPost = get_object_or_404(Post,slug=slug)
        if blogPost.author !=  author:
            return Response({'detail': 'not permited to edit'}, status=status.HTTP_403_FORBIDDEN)
        
        category  = get_object_or_404(Categories,name=selected_category)
        blogPost.title = title
        blogPost.text = text
        blogPost.html = html
        blogPost.category = category
        blogPost.image = image
        blogPost.save()
        newpost = get_object_or_404(Post,slug = slug)
        serializer = PostSerializer(newpost,context={'request': request})
        return Response({"blog":serializer.data}, status=status.HTTP_200_OK)


class FilterBlogs(APIView):
    def post(self,request,**kwargs):
        keyword = request.data.get('keyword')
        if(keyword == ""):
            return Response([], status=status.HTTP_200_OK)
        # print(keyword)
        if not keyword:
            return Response({'detail': 'Required feids are missing'}, status=status.HTTP_400_BAD_REQUEST)

        blogs = Post.objects.filter(title__contains = keyword)
        serializer = PostSerializer(blogs,context={'request': request},many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



        