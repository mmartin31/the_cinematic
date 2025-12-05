# Generated migration to add IMDB rating and rank fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='imdb_rating',
            field=models.DecimalField(decimal_places=1, default=0.0, help_text='IMDB rating from Top 1000 dataset', max_digits=3),
        ),
        migrations.AddField(
            model_name='movie',
            name='imdb_rank',
            field=models.IntegerField(blank=True, help_text='Rank in IMDB Top 1000', null=True),
        ),
    ]
