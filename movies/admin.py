from django.contrib import admin
from .models import Movie, Genre, Cast, Rating, UserProfile

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'average_rating', 'created_at')
    list_filter = ('year', 'genres')
    search_fields = ('title', 'overview')
    filter_horizontal = ('genres',)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Cast)
class CastAdmin(admin.ModelAdmin):
    list_display = ('name', 'character', 'movie', 'order')
    list_filter = ('movie',)
    search_fields = ('name', 'character')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'movie__title')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'joined_date')
    search_fields = ('user__username',)
