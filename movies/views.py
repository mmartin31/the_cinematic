# ============================================
# movies/views.py
# ============================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from .models import Movie, Genre, Rating, UserProfile
from .forms import RatingForm, UserProfileForm

def home(request):
    """Home page with trending and top-rated movies"""
    trending_movies = Movie.objects.order_by('-created_at')[:10]
    top_rated_movies = Movie.objects.order_by('-average_rating')[:8]
    
    context = {
        'trending_movies': trending_movies,
        'top_rated_movies': top_rated_movies,
    }
    return render(request, 'movies/home.html', context)


def browse(request):
    """Browse/search page with filters"""
    movies = Movie.objects.all()
    genres = Genre.objects.all()
    
    # Search query
    search_query = request.GET.get('search', '')
    if search_query:
        movies = movies.filter(
            Q(series_title__icontains=search_query) |
            Q(overview__icontains=search_query)
        )
    
    # Genre filter
    genre_filter = request.GET.get('genre', '')
    if genre_filter:
        movies = movies.filter(genres__name=genre_filter)
    
    # Year filter
    year_filter = request.GET.get('year', '')
    if year_filter:
        movies = movies.filter(released_year=year_filter)
    
    # Sort filter
    sort_by = request.GET.get('sort', '')
    if sort_by == 'rating':
        movies = movies.order_by('-average_rating', '-created_at')
    elif sort_by == 'recent':
        movies = movies.order_by('-created_at')
    elif sort_by == 'year':
        movies = movies.order_by('-released_year', 'title')
    else:
        movies = movies.order_by('-created_at')
    
    # Remove duplicates if filtering by genre
    movies = movies.distinct()
    
    # Get unique years for filter
    years = Movie.objects.values_list('released_year', flat=True).distinct().order_by('-released_year')
    
    context = {
        'movies': movies,
        'genres': genres,
        'years': years,
        'search_query': search_query,
        'selected_genre': genre_filter,
        'selected_year': year_filter,
        'sort_by': sort_by,
    }
    return render(request, 'movies/browse.html', context)


def top_rated(request):
    """Top rated movies page with leaderboard"""
    # Get all movies ordered by rating, with tiebreakers
    all_movies = Movie.objects.filter(
        average_rating__gt=0
    ).annotate(
        rating_count=Count('ratings')
    ).order_by('-average_rating', '-rating_count', '-released_year')
    
    # Genre filter
    genres = Genre.objects.all()
    genre_filter = request.GET.get('genre', '')
    if genre_filter:
        all_movies = all_movies.filter(genres__name=genre_filter)
    
    # Get top 10 for podium
    top_10 = all_movies[:10]
    
    # Get the rest for the leaderboard
    rest_movies = all_movies[10:]
    
    context = {
        'top_10': top_10,
        'rest_movies': rest_movies,
        'genres': genres,
        'selected_genre': genre_filter,
    }
    return render(request, 'movies/top_rated.html', context)


def movie_detail(request, movie_id):
    """Movie detail page"""
    movie = get_object_or_404(Movie, id=movie_id)
    similar_movies = Movie.objects.filter(
        genres__in=movie.genres.all()
    ).exclude(id=movie.id).distinct()[:4]
    
    user_rating = None
    if request.user.is_authenticated:
        try:
            user_rating = Rating.objects.get(user=request.user, movie=movie)
        except Rating.DoesNotExist:
            pass
    
    context = {
        'movie': movie,
        'similar_movies': similar_movies,
        'user_rating': user_rating,
    }
    return render(request, 'movies/movie_detail.html', context)


@login_required
def rate_movie(request, movie_id):
    """Handle movie rating submission (AJAX)"""
    if request.method == 'POST':
        movie = get_object_or_404(Movie, id=movie_id)
        rating_value = int(request.POST.get('rating', 0))
        
        if 1 <= rating_value <= 5:
            rating, created = Rating.objects.update_or_create(
                user=request.user,
                movie=movie,
                defaults={'rating': rating_value}
            )
            
            return JsonResponse({
                'success': True,
                'rating': rating_value,
                'message': 'Rating saved successfully!'
            })
        
        return JsonResponse({
            'success': False,
            'message': 'Invalid rating value'
        }, status=400)
    
    return JsonResponse({'success': False}, status=405)


@login_required
def profile(request):
    """User profile page"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    rated_movies = Rating.objects.filter(user=request.user).order_by('-created_at')
    top_rated = profile.get_top_rated_movies()
    
    context = {
        'profile': profile,
        'rated_movies': rated_movies,
        'top_rated': top_rated,
        'total_ratings': profile.get_rated_movies_count(),
        'average_rating': profile.get_average_rating(),
    }
    return render(request, 'movies/profile.html', context)


@login_required
def delete_rating(request, rating_id):
    """Delete a user's rating"""
    rating = get_object_or_404(Rating, id=rating_id, user=request.user)
    movie = rating.movie
    rating.delete()
    movie.update_average_rating()
    messages.success(request, 'Rating deleted successfully!')
    return redirect('profile')


def user_login(request):
    """Login page"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'movies/login.html', {'form': form})


def user_signup(request):
    """Signup page"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'movies/signup.html', {'form': form})


@login_required
def user_logout(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')