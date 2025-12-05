"""
Script to populate IMDB ratings from the CSV file into the Movie model
Run this after migrations: python manage.py shell < import_imdb_ratings.py
"""
import os
import sys
import re
import django
import pandas as pd


def _parse_runtime(runtime_str):
    if not runtime_str or pd.isna(runtime_str):
        return None
    m = re.search(r"(\d+)", str(runtime_str))
    return int(m.group(1)) if m else None


def main(csv_path: str = "data/imdb_top_1000.csv"):
    print(f"Importing IMDB ratings from: {csv_path}")

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "the_cinematic.settings")
    django.setup()

    from movies.models import Movie, Genre

    df = pd.read_csv(csv_path)

    updated = 0
    skipped = 0

    for index, row in df.iterrows():
        title = row.get("Series_Title") or row.get("series_title")
        if pd.isna(title) or not title:
            continue

        year = row.get("Released_Year") or row.get("released_year")
        try:
            year = int(year)
        except (ValueError, TypeError):
            continue

        # Get IMDB rating
        imdb_rating_str = row.get("IMDB_Rating") or row.get("imdb_rating")
        try:
            imdb_rating = float(imdb_rating_str) if imdb_rating_str and not pd.isna(imdb_rating_str) else 0.0
        except (ValueError, TypeError):
            imdb_rating = 0.0

        imdb_rank = index + 1 if imdb_rating > 0 else None
        
        # Parse runtime
        runtime_str = row.get("Runtime") or row.get("runtime")
        runtime = _parse_runtime(runtime_str) or 0
        
        # Get overview
        overview = row.get("Overview") or row.get("overview") or ""

        # Create or get movie by title and year
        try:
            movie, created = Movie.objects.get_or_create(
                title=title,
                year=year,
                defaults={
                    'runtime': runtime,
                    'overview': str(overview)[:1000],
                    'release_date': f"{year}-01-01",
                    'imdb_rating': imdb_rating,
                    'imdb_rank': imdb_rank,
                }
            )
            if not created:
                # Update IMDB fields if movie already exists
                movie.imdb_rating = imdb_rating
                movie.imdb_rank = imdb_rank
                movie.save()
            updated += 1
        except Exception as e:
            skipped += 1
            if skipped <= 10:  # Print first 10 errors
                print(f"  Error processing {title} ({year}): {str(e)}")

        if (index + 1) % 100 == 0:
            print(f"Processed {index+1} rows (created/updated={updated}, errors={skipped})")

    print(f"Done. Updated: {updated}, Skipped: {skipped}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/imdb_top_1000.csv"
    main(path)
