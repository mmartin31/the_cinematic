import os
import sys
import re
import django
import pandas as pd


def _int_or_none(value):
    try:
        return int(value)
    except Exception:
        return None


def _parse_runtime(runtime_str):
    if not runtime_str or pd.isna(runtime_str):
        return None
    # runtime like "142 min" -> extract digits
    m = re.search(r"(\d+)", str(runtime_str))
    return int(m.group(1)) if m else None


def _parse_gross(gross_str):
    if not gross_str or pd.isna(gross_str):
        return None
    # remove non-digits
    digits = re.sub(r"[^0-9]", "", str(gross_str))
    return int(digits) if digits else None


def main(csv_path: str = "data/imdb_top_1000.csv"):
    print(f"Importing movies from: {csv_path}")

    # Ensure project root is on sys.path so `the_cinematic` package is importable
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "the_cinematic.settings")
    django.setup()

    from movies.models import Movie, Genre
    from django.db import transaction

    df = pd.read_csv(csv_path)

    created = 0
    updated = 0
    skipped = 0

    for index, row in df.iterrows():
        # support different header casings
        title = row.get("Series_Title") or row.get("series_title") or row.get("Series title")
        if pd.isna(title):
            continue

        released_year = row.get("Released_Year") or row.get("released_year")
        released_year = _int_or_none(released_year)

        poster_link = row.get("Poster_Link") or row.get("poster_link")
        runtime = _parse_runtime(row.get("Runtime") or row.get("runtime"))

        overview = row.get("Overview") or row.get("overview") or ""
        director = row.get("Director") or row.get("director") or ""
        star1 = row.get("Star1") or row.get("star1") or ""
        star2 = row.get("Star2") or row.get("star2")
        star3 = row.get("Star3") or row.get("star3")
        star4 = row.get("Star4") or row.get("star4")

        gross = _parse_gross(row.get("Gross") or row.get("gross"))

        # tmdb id column has varied names in sources
        tmdb_id = row.get("tmdb_id") or row.get("tmbd_id") or row.get("tmdb")
        tmdb_id = _int_or_none(tmdb_id)

        # Build defaults dict for update_or_create
        defaults = {
            "poster_link": poster_link,
            "runtime": runtime,
            "overview": overview,
            "director": director,
            "star1": star1,
            "star2": star2,
            "star3": star3,
            "star4": star4,
            "gross": gross,
            "tmdb_id": tmdb_id,
        }

        # Prefer to dedupe by `tmdb_id` when available; otherwise require released_year.
        # If released_year is missing we skip the row to avoid NOT NULL constraint errors.
        if not tmdb_id and released_year is None:
            print(f"Skipping row {index+1}: missing released_year for '{title}'")
            skipped += 1
            continue

        with transaction.atomic():
            if tmdb_id:
                movie, created_flag = Movie.objects.update_or_create(
                    tmdb_id=tmdb_id,
                    defaults={**defaults, 'series_title': title, 'released_year': released_year},
                )
            else:
                movie, created_flag = Movie.objects.update_or_create(
                    series_title=title,
                    released_year=released_year,
                    defaults=defaults,
                )

            if created_flag:
                created += 1
            else:
                updated += 1

            # Handle genres (many-to-many)
            genres_field = row.get("Genre") or row.get("genres") or row.get("genre")
            if genres_field and not pd.isna(genres_field):
                # CSV stores e.g. "Action, Crime, Drama" (quoted) -> split on comma
                names = [g.strip() for g in str(genres_field).split(",") if g.strip()]
                genre_objs = []
                for name in names:
                    obj, _ = Genre.objects.get_or_create(name=name)
                    genre_objs.append(obj)
                # replace movie genres with parsed list
                movie.genres.set(genre_objs)

        if (index + 1) % 100 == 0:
            print(f"Processed {index+1} rows (created={created}, updated={updated})")

    print(f"Done. Created: {created}, Updated: {updated}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/imdb_top_1000.csv"
    main(path)
