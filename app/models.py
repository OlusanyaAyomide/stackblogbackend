from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import random
import string

# Create your models here.

class UserProfile(models.Model):
    image = models.CharField(max_length=50)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length= 100)
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    email = models.CharField(max_length=50)


class Categories(models.Model):
    name=models.CharField(max_length=30)

class Post(models.Model):
    author = models.ForeignKey(UserProfile,on_delete=models.CASCADE,related_name="posts")
    category = models.ForeignKey(Categories,on_delete=models.CASCADE,related_name="cat_post")
    createdAt=models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    image = models.CharField(max_length=200)
    text = models.CharField(max_length=5000)
    like = models.ManyToManyField(UserProfile,related_name="liked_post")
    title = models.CharField(max_length=80)
    html = models.CharField(max_length=5000)
    slug = models.CharField(unique=True,max_length=200)

    class Meta:
        ordering = ['-createdAt']


    #Generate a unique slug for every post upon saving 
    def save(self, *args, **kwargs):  
        if not self.pk:
            self.slug = slugify(self.title)
            if not self._is_unique_slug():
                self.slug = self._make_unique_slug()

        super().save(*args, **kwargs)

    def _is_unique_slug(self):
        return not Post.objects.exclude(id=self.id).filter(slug=self.slug).exists()

    def _make_unique_slug(self):
        suffix = ''.join(random.choices(string.digits, k=5)) 
        return f"{self.slug}-{suffix}"
    
   

class PostComment(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=300)
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE,related_name="user_comment")
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name="post_comment")

    class Meta:
        ordering = ['-createdAt']

