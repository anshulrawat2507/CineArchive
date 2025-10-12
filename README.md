# BollywoodLens DBMS Prototype

BollywoodLens is a movie-centric relational database built around the Indian movies dataset. This repository contains everything you need for the **Day 1 (40–50%) milestone**: schema design, ER diagram, data loading pipeline, and demo SQL artefacts.

## ✅ What you can demo tomorrow

- ER diagram (see `docs/ER_diagram.md`).
- Normalised schema with three main tables (`Movies`, `Users`, `Ratings`).
- Clean import of the ~50k movie rows.
- Aggregation queries for quick insights.
- A view, stored procedure, and trigger implemented directly in the database.

## 1. Prepare the environment

> **New to the project?** A full clone-to-demo walkthrough lives in `docs/SETUP_GUIDE.md`. Use it when publishing the repo or sharing with teammates.

1. Install MySQL 8.x locally and make sure `mysql` CLI is on your PATH.
2. Create a Python 3.11+ virtual environment (optional but recommended):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

## 2. Create database & core objects

Run the schema script inside MySQL:

```powershell
mysql -u root -p < sql\bollywoodlens_schema.sql
```

This will:

- Create the `BollywoodLens` database (safe to re-run; it drops existing copy).
- Provision tables, constraints, sample users, view, stored procedure, and trigger.

## 3. Load the movies dataset

1. Confirm the CSV is present at `data\indian movies.csv`.
2. Execute the loader script:

   ```powershell
   python scripts\load_movies.py --csv data\indian movies.csv --db-url mysql+pymysql://root:password@localhost/BollywoodLens
   ```

   - Replace `root:password` with your MySQL credentials.
   - The script cleans duration, ratings, votes, and year values before inserting.
   - Duplicate IMDb IDs are automatically upserted.

3. Validate the row count:

   ```sql
   SELECT COUNT(*) FROM Movies;
   ```

   Expect roughly 50,000 rows (depending on data cleanliness).

## 4. Demo SQL queries

After loading, switch to the database and run the insight queries:

```sql
USE BollywoodLens;

-- Top 10 Hindi movies by IMDb rating
SELECT title, imdb_rating
FROM Movies
WHERE language = 'Hindi'
ORDER BY imdb_rating DESC
LIMIT 10;

-- Average IMDb rating per genre
SELECT genre, AVG(imdb_rating) AS avg_rating
FROM Movies
WHERE imdb_rating IS NOT NULL AND genre <> ''
GROUP BY genre
ORDER BY avg_rating DESC;

-- Movies released per year
SELECT release_year, COUNT(*) AS movie_count
FROM Movies
GROUP BY release_year
ORDER BY release_year DESC;
```

## 5. Showcase DBMS artefacts

```sql
-- View
SELECT * FROM TopRatedMovies LIMIT 15;

-- Stored procedure
CALL GetMoviesByGenre('Action');

-- Trigger demo
INSERT INTO Ratings (user_id, movie_id, rating)
VALUES (1, 1, 11);  -- Expect: INVALID rating message from trigger
```

Explain during the viva:

- **View** securely exposes curated data without revealing the entire table.
- **Stored procedure** encapsulates reusable business logic to reduce app-side code.
- **Trigger** enforces data integrity rules automatically.

## 6. Explore advanced analytics (new)

Run the curated analysis set from `sql/analysis_queries.sql` for more storytelling options:

```powershell
mysql -u root -p BollywoodLens < sql\analysis_queries.sql
```

Highlights to mention:

- **Recent decade highlights:** Showcase well-rated modern films (`release_year >= 2015`).
- **Director leaderboard:** Uses `HAVING` + aggregates to keep only directors with ≥5 titles.
- **Window function demo:** `ROW_NUMBER()` surfaces the three longest movies per language.
- **Rating distribution:** Buckets IMDb scores to discuss data skew.

Prefer running a subset live in MySQL shell and referencing the rest in your printed script.

If you need sample user-generated data, seed ratings quickly:

```sql
REPLACE INTO Ratings (user_id, movie_id, rating)
VALUES (1, 28978, 9.5), (2, 22223, 9.0), (3, 29673, 8.8), (4, 7401, 9.2), (1, 22253, 9.6);
```

Follow-up insight:

```sql
SELECT m.title,
       ROUND(AVG(r.rating), 2) AS avg_user_rating,
       COUNT(*) AS rating_count
FROM Movies AS m
JOIN Ratings AS r ON m.movie_id = r.movie_id
GROUP BY m.movie_id, m.title
ORDER BY avg_user_rating DESC;
```

## 7. Normalisation highlights

- `Movies` holds movie metadata (atomic attributes).
- `Users` captures viewer demographics (future audience segmentation).
- `Ratings` is a junction table resolving the many-to-many relationship while keeping rating facts in one place.
- No composite attributes or repeating groups ⇒ 1NF.
- Non-key attributes depend fully on primary keys ⇒ 2NF.
- No transitive dependencies because user and movie details are isolated ⇒ 3NF.

## 8. Next steps (for 100% project)

- Add fact tables for runtime analytics (watch history, recommendations).
- Normalise directors/actors into dedicated tables for richer joins.
- Build a Streamlit/Flask dashboard to query the database visually.
- Train an ML model to suggest personalised movies based on ratings.

## Optional 🎨 Streamlit mini-app

Spin up the interactive dashboard while you present:

```powershell
streamlit run app\streamlit_app.py
```

Enter your database URL at the top (or set the `BOLLYWOODLENS_DB_URL` environment variable). The refreshed experience now offers:

- Hero section that frames the BollywoodLens story and shows live table metrics.
- Faceted movie search + genre insights, all driven directly from the DB.
- **SQL Playground:** run read-only queries (`SELECT`, `CALL`, etc.) and export the results on the spot.
- **DBMS Concepts tabs:**
   - View explorer for `TopRatedMovies`.
   - Stored procedure runner for `GetMoviesByGenre`.
   - Trigger tester that demonstrates the rating guardrail.

Keep it running on a side monitor while you talk through the schema and queries—it reinforces how the backend powers the UI.

Show up with confidence—this setup highlights solid DBMS concepts while leaving room for future enhancements.
