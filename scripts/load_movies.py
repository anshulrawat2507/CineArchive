"""Bulk-load Indian movies dataset into the BollywoodLens database.

Usage example:
    python load_movies.py --csv ..\\data\\indian_movies.csv --db-url mysql+pymysql://root:password@localhost/BollywoodLens

The script performs light cleaning to harmonise column names with the Movies table schema.
"""
from __future__ import annotations

import argparse
import math
import pathlib
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import insert

MOVIE_COLUMN_MAP = {
    "ID": "imdb_id",
    "Movie Name": "title",
    "Genre": "genre",
    "Language": "language",
    "Year": "release_year",
    "Timing(min)": "duration_minutes",
    "Rating(10)": "imdb_rating",
    "Votes": "votes",
}


def _clean_duration(value: str) -> Optional[int]:
    if pd.isna(value):
        return None
    value = str(value).strip()
    if not value or value == "-":
        return None
    digits = "".join(ch for ch in value if ch.isdigit())
    return int(digits) if digits else None


def _clean_rating(value: str) -> Optional[float]:
    if pd.isna(value):
        return None
    value = str(value).strip()
    if not value or value == "-":
        return None
    try:
        return round(float(value), 1)
    except ValueError:
        return None


def _clean_votes(value: str) -> Optional[int]:
    if pd.isna(value):
        return None
    value = str(value).strip().replace(",", "")
    if not value or value == "-":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _clean_year(value: str) -> Optional[int]:
    if pd.isna(value):
        return None
    value = str(value).strip()
    if not value or not value.isdigit():
        return None
    year_int = int(value)
    return year_int if 1900 <= year_int <= 2100 else None


def load_movies(csv_path: pathlib.Path, db_url: str, chunk_size: int = 2000) -> int:
    df = pd.read_csv(csv_path)
    missing_cols = set(MOVIE_COLUMN_MAP.keys()) - set(df.columns)
    if missing_cols:
        raise ValueError(f"CSV is missing expected columns: {sorted(missing_cols)}")

    df = df.rename(columns=MOVIE_COLUMN_MAP)

    if "duration_minutes" in df.columns:
        df["duration_minutes"] = df["duration_minutes"].apply(_clean_duration)
    else:
        df["duration_minutes"] = None

    if "imdb_rating" in df.columns:
        df["imdb_rating"] = df["imdb_rating"].apply(_clean_rating)
    else:
        df["imdb_rating"] = None

    if "votes" in df.columns:
        df["votes"] = df["votes"].apply(_clean_votes)
    else:
        df["votes"] = None

    if "release_year" in df.columns:
        df["release_year"] = df["release_year"].apply(_clean_year)
    else:
        df["release_year"] = None

    df["genre"] = (
        df["genre"] if "genre" in df.columns else pd.Series([""] * len(df))
    ).fillna("").astype(str).str.strip()

    df["language"] = (
        df["language"] if "language" in df.columns else pd.Series([""] * len(df))
    ).fillna("").astype(str).str.strip().str.title()

    df["title"] = df["title"].fillna("").astype(str).str.strip()

    if "director" not in df.columns:
        df["director"] = pd.Series([None] * len(df))
    else:
        df["director"] = df["director"].fillna("").astype(str).str.strip()

    if "actors" not in df.columns:
        df["actors"] = pd.Series([None] * len(df))
    else:
        df["actors"] = df["actors"].fillna("").astype(str).str.strip()

    df = df[df["title"] != ""]

    df = df.drop_duplicates(subset=["imdb_id"])  # maintain unique key constraint

    for col in ("duration_minutes", "votes", "release_year"):
        if col in df.columns:
            df[col] = df[col].astype("Int64")
    if "imdb_rating" in df.columns:
        df["imdb_rating"] = df["imdb_rating"].astype(float)

    # Replace pandas NA/NaN with actual None so SQLAlchemy inserts NULLs cleanly
    df = df.where(pd.notnull(df), None)

    engine = create_engine(db_url)
    inserted_rows = 0

    with engine.begin() as connection:
        for start in range(0, len(df), chunk_size):
            chunk = df.iloc[start:start + chunk_size]
            if chunk.empty:
                continue
            chunk = chunk.replace({pd.NA: None})
            chunk = chunk.where(pd.notnull(chunk), None)
            chunk = chunk.astype(object)
            records = chunk.to_dict(orient="records")
            for row in records:
                for key, value in row.items():
                    if isinstance(value, float) and math.isnan(value):
                        row[key] = None
            stmt = insert(MoviesTable.__table__).values(records)
            update_mapping = {
                col.name: stmt.inserted[col.name]
                for col in MoviesTable.__table__.columns
                if col.name not in {"movie_id", "created_at", "updated_at"}
            }
            stmt = stmt.on_duplicate_key_update(**update_mapping)
            result = connection.execute(stmt)
            inserted_rows += result.rowcount or 0
    return inserted_rows


# SQLAlchemy table reflection using declarative base -------------------------
from sqlalchemy.orm import declarative_base  # noqa: E402  (import after pandas)
from sqlalchemy import Column, Integer, String, Text, Numeric, TIMESTAMP

Base = declarative_base()


class MoviesTable(Base):
    __tablename__ = "Movies"

    movie_id = Column(Integer, primary_key=True, autoincrement=True)
    imdb_id = Column(String(12), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    genre = Column(String(255))
    language = Column(String(100))
    release_year = Column(Integer)
    duration_minutes = Column(Integer)
    director = Column(String(255))
    actors = Column(Text)
    imdb_rating = Column(Numeric(3, 1))
    votes = Column(Integer)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load movies into BollywoodLens database.")
    parser.add_argument("--csv", type=pathlib.Path, required=True, help="Path to indian movies CSV")
    parser.add_argument(
        "--db-url",
        type=str,
        required=True,
        help="SQLAlchemy database URL, e.g. mysql+pymysql://user:password@localhost/BollywoodLens",
    )
    parser.add_argument("--chunk-size", type=int, default=2000, help="Number of records per batch insert")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = load_movies(args.csv, args.db_url, args.chunk_size)
    print(f"Inserted or updated {rows} movie records.")


if __name__ == "__main__":
    main()
