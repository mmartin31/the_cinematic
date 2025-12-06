# ============================================
# movies/tests.py
# Complete Automated Test Suite
# ============================================

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date
from .models import Movie, Genre, Cast, Rating, UserProfile

# ============================================
# MODEL TESTS
# ============================================

class MovieModelTest(TestCase):
    """Test Movie model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.movie = Movie.objects.create(
            series_title="Test Movie",
            released_year=2024,
            runtime=120,
            director="Test Director",
            star1="Test Actor",
            overview="A test movie for testing purposes.",
            imdb_rating=8.5,
            average_rating=8.5
        )
    
    def test_movie_creation(self):
        """Test movie is created correctly"""
        self.assertEqual(self.movie.title, "Test Movie")
        self.assertEqual(self.movie.year, 2024)
        self.assertEqual(self.movie.runtime, 120)
        self.assertTrue(isinstance(self.movie, Movie))
    
    def test_movie_str(self):
        """Test string representation"""
        self.assertEqual(str(self.movie), "Test Movie (2024)")
    
    def test_movie_ordering(self):
        """Test movies are ordered by year and title"""
        movie2 = Movie.objects.create(
            series_title="Another Movie",
            released_year=2023,
            runtime=100,
            director="Test Director",
            star1="Test Actor",
            imdb_rating=7.5,
            overview="Another test movie."
        )
        movies = Movie.objects.all()
        self.assertEqual(movies[0], self.movie)  # 2024 comes first
        self.assertEqual(movies[1], movie2)
    
    def test_update_average_rating(self):
        """Test average rating calculation"""
        user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Create rating
        Rating.objects.create(
            user=user,
            movie=self.movie,
            rating=5
        )
        
        # Check average was updated
        self.movie.refresh_from_db()
        self.assertEqual(float(self.movie.average_rating), 5.0)


class GenreModelTest(TestCase):
    """Test Genre model functionality"""
    
    def setUp(self):
        self.genre = Genre.objects.create(name="Action")
        self.movie = Movie.objects.create(
            series_title="Action Movie",
            released_year=2024,
            runtime=120,
            director="Test Director",
            star1="Test Actor",
            imdb_rating=8.0,
            overview="An action-packed movie."
        )
    
    def test_genre_creation(self):
        """Test genre is created correctly"""
        self.assertEqual(self.genre.name, "Action")
        self.assertTrue(isinstance(self.genre, Genre))
    
    def test_genre_str(self):
        """Test string representation"""
        self.assertEqual(str(self.genre), "Action")
    
    def test_genre_movie_relationship(self):
        """Test many-to-many relationship with movies"""
        self.movie.genres.add(self.genre)
        self.assertIn(self.genre, self.movie.genres.all())
        self.assertIn(self.movie, self.genre.movies.all())


class RatingModelTest(TestCase):
    """Test Rating model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.movie = Movie.objects.create(
            series_title="Test Movie",
            released_year=2024,
            runtime=120,
            director="Test Director",
            star1="Test Actor",
            imdb_rating=8.0,
            overview="Test movie."
        )
    
    def test_rating_creation(self):
        """Test rating is created and calculates average correctly"""
        rating = Rating.objects.create(
            user=self.user,
            movie=self.movie,
            rating=5
        )
        
        # Rating should be 5
        self.assertEqual(float(rating.rating), 5.0)
    
    def test_rating_str(self):
        """Test string representation"""
        rating = Rating.objects.create(
            user=self.user,
            movie=self.movie,
            rating=5
        )
        self.assertEqual(str(rating), "testuser rated Test Movie: 5/5")
    
    def test_rating_unique_constraint(self):
        """Test user can only rate a movie once"""
        Rating.objects.create(
            user=self.user,
            movie=self.movie,
            rating=5
        )
        
        # Try to create duplicate - should use update_or_create in views
        rating2, created = Rating.objects.update_or_create(
            user=self.user,
            movie=self.movie,
            defaults={'rating': 3}
        )
        
        self.assertFalse(created)  # Should update, not create
        self.assertEqual(Rating.objects.filter(user=self.user, movie=self.movie).count(), 1)
    
    def test_rating_updates_movie_average(self):
        """Test that creating a rating updates movie average"""
        Rating.objects.create(
            user=self.user,
            movie=self.movie,
            rating=5
        )
        
        self.movie.refresh_from_db()
        self.assertEqual(float(self.movie.average_rating), 5.0)
    
    def test_get_rating_value(self):
        """Test rating value is stored correctly"""
        rating = Rating.objects.create(
            user=self.user,
            movie=self.movie,
            rating=5
        )
        
        self.assertEqual(rating.rating, 5)


class UserProfileModelTest(TestCase):
    """Test UserProfile model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.profile = UserProfile.objects.create(user=self.user)
    
    def test_profile_creation(self):
        """Test profile is created correctly"""
        self.assertEqual(self.profile.user, self.user)
        self.assertTrue(isinstance(self.profile, UserProfile))
    
    def test_profile_str(self):
        """Test string representation"""
        self.assertEqual(str(self.profile), "testuser's Profile")
    
    def test_get_rated_movies_count(self):
        """Test getting count of rated movies"""
        movie1 = Movie.objects.create(
            series_title="Movie 1", released_year=2024, runtime=120,
            director="Test Director", star1="Test Actor",
            overview="Test"
        )
        movie2 = Movie.objects.create(
            series_title="Movie 2", released_year=2024, runtime=120,
            director="Test Director", star1="Test Actor",
            overview="Test"
        )
        
        Rating.objects.create(
            user=self.user, movie=movie1,
            rating=5
        )
        Rating.objects.create(
            user=self.user, movie=movie2,
            rating=4
        )
        
        self.assertEqual(self.profile.get_rated_movies_count(), 2)


# ============================================
# VIEW TESTS
# ============================================

class HomeViewTest(TestCase):
    """Test home page view"""
    
    def setUp(self):
        self.client = Client()
        # Create test movies
        for i in range(5):
            Movie.objects.create(
                series_title=f"Movie {i}",
                released_year=2024,
                runtime=120,
                director="Test Director",
                star1="Test Actor",
                imdb_rating=8.0 + i * 0.1,
                overview="Test movie",
                average_rating=8.0 + i * 0.1
            )
    
    def test_home_page_status_code(self):
        """Test home page returns 200"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_home_page_template(self):
        """Test correct template is used"""
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'movies/home.html')
    
    def test_home_page_context(self):
        """Test context contains trending and top rated movies"""
        response = self.client.get(reverse('home'))
        self.assertIn('trending_movies', response.context)
        self.assertIn('top_rated_movies', response.context)
    
    def test_home_page_displays_movies(self):
        """Test movies are displayed on home page"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, "Movie 0")


class BrowseViewTest(TestCase):
    """Test browse page view"""
    
    def setUp(self):
        self.client = Client()
        self.genre_action = Genre.objects.create(name="Action")
        self.genre_drama = Genre.objects.create(name="Drama")
        
        self.movie1 = Movie.objects.create(
            series_title="Action Movie",
            released_year=2024,
            runtime=120,
            director="Test Director",
            star1="Test Actor",
            imdb_rating=8.0,
            overview="An action movie"
        )
        self.movie1.genres.add(self.genre_action)
        
        self.movie2 = Movie.objects.create(
            series_title="Drama Movie",
            released_year=2023,
            runtime=130,
            director="Test Director",
            star1="Test Actor",
            imdb_rating=7.5,
            overview="A drama movie"
        )
        self.movie2.genres.add(self.genre_drama)
    
    def test_browse_page_status_code(self):
        """Test browse page returns 200"""
        response = self.client.get(reverse('browse'))
        self.assertEqual(response.status_code, 200)
    
    def test_browse_page_template(self):
        """Test correct template is used"""
        response = self.client.get(reverse('browse'))
        self.assertTemplateUsed(response, 'movies/browse.html')
    
    def test_search_functionality(self):
        """Test search filter works"""
        response = self.client.get(reverse('browse'), {'search': 'Action'})
        self.assertContains(response, "Action Movie")
        self.assertNotContains(response, "Drama Movie")
    
    def test_genre_filter(self):
        """Test genre filter works"""
        response = self.client.get(reverse('browse'), {'genre': 'Action'})
        self.assertContains(response, "Action Movie")
        self.assertNotContains(response, "Drama Movie")
    
    def test_year_filter(self):
        """Test year filter works"""
        response = self.client.get(reverse('browse'), {'year': '2024'})
        self.assertContains(response, "Action Movie")
        self.assertNotContains(response, "Drama Movie")


class MovieDetailViewTest(TestCase):
    """Test movie detail page view"""
    
    def setUp(self):
        self.client = Client()
        self.movie = Movie.objects.create(
            series_title="Test Movie",
            released_year=2024,
            runtime=120,
            director="Test Director",
            star1="Test Actor",
            imdb_rating=8.0,
            overview="A test movie for testing."
        )
    
    def test_movie_detail_status_code(self):
        """Test movie detail page returns 200"""
        response = self.client.get(reverse('movie_detail', args=[self.movie.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_movie_detail_template(self):
        """Test correct template is used"""
        response = self.client.get(reverse('movie_detail', args=[self.movie.id]))
        self.assertTemplateUsed(response, 'movies/movie_detail.html')
    
    def test_movie_detail_context(self):
        """Test context contains movie"""
        response = self.client.get(reverse('movie_detail', args=[self.movie.id]))
        self.assertEqual(response.context['movie'], self.movie)
    
    def test_movie_detail_404(self):
        """Test non-existent movie returns 404"""
        response = self.client.get(reverse('movie_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)


class TopRatedViewTest(TestCase):
    """Test top rated page view"""
    
    def setUp(self):
        self.client = Client()
        # Create movies with different ratings
        for i in range(15):
            Movie.objects.create(
                series_title=f"Movie {i}",
                released_year=2024,
                runtime=120,
                director="Test Director",
                star1="Test Actor",
                imdb_rating=9.0 - (i * 0.1),
                overview="Test",
                average_rating=9.0 - (i * 0.1)  # Descending ratings
            )
    
    def test_top_rated_status_code(self):
        """Test top rated page returns 200"""
        response = self.client.get(reverse('top_rated'))
        self.assertEqual(response.status_code, 200)
    
    def test_top_rated_template(self):
        """Test correct template is used"""
        response = self.client.get(reverse('top_rated'))
        self.assertTemplateUsed(response, 'movies/top_rated.html')
    
    def test_top_rated_ordering(self):
        """Test movies are ordered by rating"""
        response = self.client.get(reverse('top_rated'))
        top_10 = response.context['top_10']
        
        # Check first movie has highest rating
        self.assertEqual(top_10[0].title, "Movie 0")
        self.assertEqual(float(top_10[0].average_rating), 9.0)


class AuthenticationTest(TestCase):
    """Test authentication views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_login_page_status_code(self):
        """Test login page returns 200"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_signup_page_status_code(self):
        """Test signup page returns 200"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_functionality(self):
        """Test user can login"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
    
    def test_logout_functionality(self):
        """Test user can logout"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
    
    def test_signup_creates_user(self):
        """Test signup creates new user"""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'newtestpass123',
            'password2': 'newtestpass123'
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())


class RatingViewTest(TestCase):
    """Test rating functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.movie = Movie.objects.create(
            series_title="Test Movie",
            released_year=2024,
            runtime=120,
            director="Test Director",
            star1="Test Actor",
            imdb_rating=8.0,
            overview="Test"
        )
    
    def test_rate_movie_requires_login(self):
        """Test rating requires authentication"""
        response = self.client.post(reverse('rate_movie', args=[self.movie.id]), {
            'story_rating': 5,
            'acting_rating': 5,
            'cinematography_rating': 5,
            'soundtrack_rating': 5,
            'direction_rating': 5
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_rate_movie_creates_rating(self):
        """Test rating is created successfully"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('rate_movie', args=[self.movie.id]), {
            'rating': 5
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Check rating was created
        self.assertTrue(Rating.objects.filter(user=self.user, movie=self.movie).exists())
        rating = Rating.objects.get(user=self.user, movie=self.movie)
        self.assertEqual(float(rating.rating), 5.0)
    
    def test_rate_movie_updates_existing(self):
        """Test rating can be updated"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create initial rating
        Rating.objects.create(
            user=self.user,
            movie=self.movie,
            rating=3
        )
        
        # Update rating
        response = self.client.post(reverse('rate_movie', args=[self.movie.id]), {
            'rating': 5
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Check only one rating exists and it's updated
        self.assertEqual(Rating.objects.filter(user=self.user, movie=self.movie).count(), 1)
        rating = Rating.objects.get(user=self.user, movie=self.movie)
        self.assertEqual(float(rating.rating), 5.0)


class ProfileViewTest(TestCase):
    """Test profile page view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user)
    
    def test_profile_requires_login(self):
        """Test profile page requires authentication"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_page_status_code(self):
        """Test logged-in user can access profile"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
    
    def test_profile_shows_ratings(self):
        """Test profile displays user's ratings"""
        self.client.login(username='testuser', password='testpass123')
        
        movie = Movie.objects.create(
            series_title="Rated Movie",
            released_year=2024,
            runtime=120,
            director="Test Director",
            star1="Test Actor",
            imdb_rating=8.5,
            overview="Test"
        )
        
        Rating.objects.create(
            user=self.user,
            movie=movie,
            rating=5
        )
        
        response = self.client.get(reverse('profile'))
        self.assertContains(response, "Rated Movie")


# ============================================
# RUN TESTS COMMAND
# ============================================

"""
To run all tests:
    python manage.py test movies

To run specific test class:
    python manage.py test movies.tests.MovieModelTest

To run specific test method:
    python manage.py test movies.tests.MovieModelTest.test_movie_creation

To run with verbosity:
    python manage.py test movies -v 2

To run with coverage (install: pip install coverage):
    coverage run --source='.' manage.py test movies
    coverage report
    coverage html  # Creates htmlcov/index.html
"""