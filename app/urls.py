from django.urls import path
from . import views

urlpatterns=[
    path("auth/login",views.Create_LogIn().as_view()),
    path("profile",views.GetProfile().as_view()),
    path("blog/create",views.CreateNewBlog().as_view()),
    path("blogs/all",views.GetAllPosts().as_view()),
    path("blog/like",views.LikePost().as_view()),
    path("blog/comment",views.CommentOnPost().as_view()),
    path("blog/edit",views.EditBlog.as_view()),
    path("blog/search",views.FilterBlogs.as_view()),
    path("blog/<str:slug>",views.BlogDetail.as_view()),
    
]