from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=200)
    year = models.IntegerField()
    runtime = models.IntegerField(help_text="Runtime in minutes")
    overview = models.TextField()
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    backdrop = models.ImageField(upload_to='backdrops/', blank=True, null=True)
    release_date = models.DateField()
    genres = models.ManyToManyField(Genre, related_name='movies', blank=True)
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', 'title']

    def __str__(self):
        return f"{self.title} ({self.year})"

    def update_average_rating(self):
        """Calculate and update the average rating"""
        ratings = self.ratings.all()
        if ratings:
            avg = sum(r.rating for r in ratings) / len(ratings)
            self.average_rating = round(avg, 1)
            self.save()


class Cast(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='cast')
    name = models.CharField(max_length=200)
    character = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='cast/', blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Cast Members"

    def __str__(self):
        return f"{self.name} as {self.character}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} rated {self.movie.title}: {self.rating}/5"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.movie.update_average_rating()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    joined_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_top_rated_movies(self):
        """Get user's top 5 rated movies"""
        return self.user.ratings.filter(rating=5).order_by('-created_at')[:5]

    def get_rated_movies_count(self):
        """Get total number of movies rated by user"""
        return self.user.ratings.count()

    def get_average_rating(self):
        """Get user's average rating"""
        ratings = self.user.ratings.all()
        if ratings:
            return round(sum(r.rating for r in ratings) / len(ratings), 1)
        return 0.0