"""Interactive Streamlit UI to explore the BollywoodLens database.

Run with:
    streamlit run app/streamlit_app.py

Update the DB_URL constant or pass --db-url at runtime to connect using your credentials.
"""
from __future__ import annotations

import os
from typing import Optional, Tuple

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

DEFAULT_DB_URL = "mysql+pymysql://root:password@localhost/BollywoodLens"


def get_engine(db_url: Optional[str]):
    engine_url = db_url or os.getenv("BOLLYWOODLENS_DB_URL", DEFAULT_DB_URL)
    return create_engine(engine_url, pool_pre_ping=True)


def fetch_dataframe(engine, query: str, **params) -> pd.DataFrame:
    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        if result.returns_rows:
            return pd.DataFrame(result.fetchall(), columns=result.keys())
        return pd.DataFrame()


def fetch_scalar(engine, query: str, **params):
    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        return result.scalar()


def execute_sql(engine, query: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Run a read-only SQL statement and return (dataframe, message)."""

    stripped = query.strip()
    if not stripped:
        return None, "Please enter a SQL statement."

    allowed_prefixes = ("select", "with", "show", "describe", "explain", "call")
    first_token = stripped.split(None, 1)[0].lower()
    if not first_token.startswith(allowed_prefixes):
        return None, "Only read-only queries (SELECT/SHOW/DESCRIBE/CALL/EXPLAIN) are allowed in the playground."

    with engine.connect() as conn:
        result = conn.execute(text(query))
        if result.returns_rows:
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df, None
        return None, "Query executed but did not return any rows."


def main() -> None:
    st.set_page_config(page_title="BollywoodLens Explorer", layout="wide")
    st.title("🎬 BollywoodLens Explorer")
    st.markdown(
        """
        *BollywoodLens* is a movie-centric relational database crafted to showcase DBMS fundamentals.
        Connect below, explore the data warehouse, and experiment with read-only SQL in a safe playground.
        """
    )

    db_url = st.text_input(
        "Database URL",
        value=DEFAULT_DB_URL,
        help="SQLAlchemy-style connection string",
    )
    if not db_url:
        st.warning("Please provide a database URL to continue.")
        st.stop()

    engine = get_engine(db_url)

    st.subheader("Database snapshot")
    col1, col2, col3 = st.columns(3)
    try:
        movie_count = fetch_scalar(engine, "SELECT COUNT(*) FROM Movies;")
        rating_count = fetch_scalar(engine, "SELECT COUNT(*) FROM Ratings;")
        avg_rating = fetch_scalar(
            engine,
            "SELECT ROUND(AVG(imdb_rating), 2) FROM Movies WHERE imdb_rating IS NOT NULL;",
        )
    except SQLAlchemyError as exc:  # pragma: no cover - user feedback
        st.error(f"Connection failed: {exc}")
        st.stop()

    col1.metric("Movies", f"{movie_count:,}" if movie_count is not None else "—")
    col2.metric("Ratings", f"{rating_count:,}" if rating_count is not None else "—")
    col3.metric("Avg IMDb rating", avg_rating if avg_rating is not None else "—")

    st.header("Search movies")
    search_title = st.text_input("Movie title contains")
    selected_language = st.selectbox(
        "Language",
        options=["All", "Hindi", "English", "Tamil", "Telugu", "Malayalam", "Kannada", "Marathi"],
        index=0,
    )
    min_rating = st.slider(
        "Minimum IMDb rating",
        min_value=0.0,
        max_value=10.0,
        value=7.0,
        step=0.1,
    )

    query = """
        SELECT title, genre, language, release_year, imdb_rating
        FROM Movies
        WHERE (:title = '' OR title LIKE CONCAT('%', :title, '%'))
          AND (:language = 'All' OR language = :language)
          AND (imdb_rating IS NULL OR imdb_rating >= :rating)
        ORDER BY imdb_rating DESC
        LIMIT 100;
    """

    df_movies = fetch_dataframe(
        engine,
        query,
        title=search_title.strip(),
        language=selected_language,
        rating=min_rating,
    )
    st.dataframe(df_movies, use_container_width=True)

    st.header("Average rating by genre")
    genre_query = """
        SELECT genre, AVG(imdb_rating) AS avg_rating, COUNT(*) AS movie_count
        FROM Movies
        WHERE imdb_rating IS NOT NULL AND genre <> ''
        GROUP BY genre
        ORDER BY avg_rating DESC
        LIMIT 20;
    """
    df_genre = fetch_dataframe(engine, genre_query)
    if not df_genre.empty:
        st.bar_chart(df_genre.set_index("genre")["avg_rating"], height=400)
        with st.expander("Show genre table"):
            st.dataframe(df_genre, use_container_width=True)
    else:
        st.info("No genre data available to chart.")

    st.header("SQL playground (read-only)")
    default_sql = "SELECT title, imdb_rating FROM Movies ORDER BY imdb_rating DESC LIMIT 10;"
    user_sql = st.text_area("Write a SQL query", value=default_sql, height=180)
    if st.button("Run SQL"):
        df_result, message = execute_sql(engine, user_sql)
        if message:
            st.info(message)
        elif df_result is not None and not df_result.empty:
            st.success(f"Returned {len(df_result)} rows")
            st.dataframe(df_result, use_container_width=True)
            st.download_button(
                label="Download results as CSV",
                data=df_result.to_csv(index=False).encode("utf-8"),
                file_name="bollywoodlens_query.csv",
                mime="text/csv",
            )
        else:
            st.warning("No rows to display.")

    st.header("DBMS concepts in action")
    view_tab, proc_tab, trigger_tab = st.tabs([
        "View: TopRatedMovies",
        "Stored Procedure",
        "Trigger",
    ])

    with view_tab:
        st.write("The `TopRatedMovies` view publishes curated high-rated titles for downstream apps.")
        view_rating = st.slider(
            "Only show ratings from",
            min_value=7.0,
            max_value=10.0,
            value=8.5,
            step=0.1,
            key="view_rating",
        )
        view_query = """
            SELECT title, genre, release_year, imdb_rating
            FROM TopRatedMovies
            WHERE imdb_rating >= :rating
            ORDER BY imdb_rating DESC, release_year DESC
            LIMIT 50;
        """
        df_view = fetch_dataframe(engine, view_query, rating=view_rating)
        st.dataframe(df_view, use_container_width=True)

    with proc_tab:
        st.write("`GetMoviesByGenre` encapsulates reusable business logic with sorting baked in.")
        genre_input = st.text_input("Genre keyword", value="Thriller", key="proc_genre")
        if st.button("Run stored procedure", key="proc_button"):
            proc_query = "CALL GetMoviesByGenre(:genre);"
            df_proc = fetch_dataframe(engine, proc_query, genre=genre_input.strip())
            st.dataframe(df_proc, use_container_width=True)

    with trigger_tab:
        st.write("`BeforeRatingInsert` stops invalid ratings before they pollute the table.")
        trigger_rating = st.number_input(
            "Try inserting a rating",
            min_value=0.0,
            max_value=11.0,
            value=10.5,
            step=0.1,
        )
        if st.button("Test trigger"):
            insert_sql = """
                INSERT INTO Ratings (user_id, movie_id, rating)
                VALUES (:user_id, :movie_id, :rating);
            """
            try:
                with engine.begin() as conn:
                    conn.execute(
                        text(insert_sql),
                        {
                            "user_id": 1,
                            "movie_id": 1,
                            "rating": trigger_rating,
                        },
                    )
                st.success("Rating accepted — trigger conditions satisfied.")
            except SQLAlchemyError as exc:
                st.error(f"Trigger blocked the insert: {exc}")
                st.info("Try a value greater than 10 to see the trigger fire.")

    st.caption("BollywoodLens · Streamlit demo · DB-backed search, analytics & DBMS artefacts")


if __name__ == "__main__":
    main()
