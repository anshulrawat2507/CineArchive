# BollywoodLens Demo Script (40–50% Milestone)

Use this script as a structured walkthrough during your evaluation. Adjust the timings to match your slot (target 5–7 minutes).

---

## 0. Setup Checks (before entering the room)
- MySQL service is running and `BollywoodLens` database exists.
- Streamlit app running on localhost (optional wow factor).
- Terminal window open with MySQL shell ready.
- Dataset successfully loaded (`SELECT COUNT(*) FROM Movies;`).

## 1. Introduction (45 seconds)
> “Ma’am/Sir, welcome to BollywoodLens — our DBMS-centric movie recommendation foundation. Today we’re presenting the core database layer, covering design, normalization, ingestion of ~50k Indian movies, and key SQL artefacts like views, stored procedures, and triggers.”

Highlight project scope: scalable catalog, users, and ratings to support future analytics/ML.

## 2. ER Diagram & Normalization (60 seconds)
- Open `docs/ER_diagram.md` (Mermaid render or exported PNG).
- Explain entities:
  - **Movies**: master catalog with unique IMDb IDs.
  - **Users**: simulated viewer profiles.
  - **Ratings**: junction table enabling many-to-many relationship.
- Normalization checkpoints:
  - 1NF: atomic attributes, no repeating groups.
  - 2NF: non-key attributes depend on full primary key.
  - 3NF: movies and users separated, preventing transitive dependencies.

## 3. Table Structures (60 seconds)
In MySQL shell:
```sql
USE BollywoodLens;
DESCRIBE Movies;
DESCRIBE Users;
DESCRIBE Ratings;
```
Point out primary/foreign keys, checks, timestamps.

## 4. Data Loading Evidence (45 seconds)
- Command: `SELECT COUNT(*) FROM Movies;` (expect ≈50,000).
- Mention cleaning script `scripts/load_movies.py` (pandas + SQLAlchemy) for repeatable ingestion and duplicate handling.
- Optional: show snippet of code to highlight data cleaning logic.

## 5. Insight Queries (90 seconds)
Run and interpret quickly:
```sql
-- 5.1 Top 10 Hindi movies
SELECT title, imdb_rating
FROM Movies
WHERE language = 'Hindi'
ORDER BY imdb_rating DESC
LIMIT 10;

-- 5.2 Avg rating per genre
SELECT genre, AVG(imdb_rating) AS avg_rating
FROM Movies
WHERE imdb_rating IS NOT NULL AND genre <> ''
GROUP BY genre
ORDER BY avg_rating DESC;

-- 5.3 Movies released per year
SELECT release_year, COUNT(*) AS movie_count
FROM Movies
GROUP BY release_year
ORDER BY release_year DESC;
```
Explain how these demonstrate aggregation, filtering, and group analysis in DBMS.

## 6. Advanced Analysis (75 seconds)

- Mention `sql/analysis_queries.sql` and pick one highlight (e.g., director leaderboard).
- Run live:
  ```sql
  SELECT director,
         COUNT(*) AS movie_count,
         ROUND(AVG(imdb_rating), 2) AS avg_rating
  FROM Movies
  WHERE director IS NOT NULL AND imdb_rating IS NOT NULL
  GROUP BY director
  HAVING COUNT(*) >= 5
  ORDER BY avg_rating DESC
  LIMIT 5;
  ```
- Tie insight back to recommendation potential.

## 7. Advanced DBMS Artefacts (90 seconds)
- **View**:
  ```sql
  SELECT * FROM TopRatedMovies LIMIT 10;
  ```
  Mention security & reuse advantages.

- **Stored Procedure**:
  ```sql
  CALL GetMoviesByGenre('Thriller');
  ```
  Emphasize encapsulated logic and performance benefits.

- **Trigger**:
  ```sql
  INSERT INTO Ratings (user_id, movie_id, rating) VALUES (1, 1, 11);
  ```
  Expect custom error → demonstrates integrity enforcement.

## 8. Optional UI Showcase (60 seconds)
- Switch to Streamlit app (`streamlit run app/streamlit_app.py`).
- Walk through: hero metrics → faceted movie search → genre chart.
- Open the SQL Playground to execute a custom `SELECT` live and download the CSV.
- Demonstrate the View/Procedure/Trigger tabs briefly (e.g., run the stored procedure, show trigger rejection message).
- Reinforce that DB remains the single source of truth.

## 9. Roadmap (45 seconds)
> “Next, we’ll build personalized recommendations by extending the ratings table, add dedicated actor/director entities, and connect a frontend/mobile client. The database layer already supports these future modules.”

## 10. Q&A Buffer
Keep the terminal open with schema file and loader script ready for deeper questions.

---

### Handy Reminders
- Credentials: update `DEFAULT_DB_URL` or environment variable before demo.
- Backup Plan: export ER diagram as image in case Mermaid rendering is blocked.
- Troubleshooting catchphrases: “Our trigger prevents inconsistent ratings”, “Views help us expose curated datasets safely.”
