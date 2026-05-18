from django.contrib import admin
from .models import UserProfile, Tag, Photo, Like


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    list_display = ['name', 'slug']


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_by', 'uploaded_at', 'total_likes', 'total_dislikes']
    list_filter = ['tags', 'uploaded_at']
    search_fields = ['title', 'description']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'photo', 'value', 'created_at']
    list_filter = ['value']
