from django.contrib import admin
from .models import Categories,Post,PostComment,UserProfile


admin.site.register(Categories)
admin.site.register(Post)
admin.site.register(PostComment)
admin.site.register(UserProfile)

# Register your models here.
