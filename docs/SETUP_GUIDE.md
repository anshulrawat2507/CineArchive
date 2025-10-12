# Project Setup & Usage Guide

Follow these steps to clone the repository, provision the database, load the dataset, and launch the Streamlit frontend locally. The instructions assume Windows PowerShell, but the equivalent commands for macOS/Linux are noted where helpful.

---

## 1. Prerequisites

| Requirement | Notes |
|-------------|-------|
| Python 3.11+ | Required for the data loader and Streamlit UI. |
| MySQL 8.x server | The schema and scripts expect MySQL 8 features. |
| Git | Needed to clone the repository. |
| (Optional) Streamlit | Installed automatically from `requirements.txt`. |

---

## 2. Clone the repository

```powershell
cd <your-working-directory>
git clone https://github.com/<your-org-or-username>/<your-repo-name>.git
cd <your-repo-name>
```

If you downloaded a ZIP instead of cloning, extract it and move into the root folder before continuing.

---

## 3. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

_On macOS/Linux:_
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 4. Install Python dependencies

```powershell
pip install -r requirements.txt
```

This pulls in `pandas`, `SQLAlchemy`, `PyMySQL`, `streamlit`, and `cryptography` (needed for MySQL’s default auth plugin).

---

## 5. Configure database credentials

Decide how you want the scripts to connect to MySQL:

- **Option A – Environment variable (recommended):**

  ```powershell
  setx BOLLYWOODLENS_DB_URL "mysql+pymysql://<user>:<password>@localhost/BollywoodLens"
  ```

  Replace `<user>` / `<password>` with your credentials. Reopen the terminal so the value is picked up.

- **Option B – Inline arguments:** Supply `--db-url` when running Python scripts or edit `DEFAULT_DB_URL` in `app/streamlit_app.py`.

---

## 6. Create the database schema

Launch the MySQL CLI and run the provided schema script:

```powershell
mysql -u <user> -p < sql\bollywoodlens_schema.sql
```

This command will:

1. Drop any existing `BollywoodLens` database (safe for development).
2. Create the database with UTF-8 settings.
3. Provision the `Movies`, `Users`, and `Ratings` tables plus a demo view, stored procedure, and trigger.

You can verify with:
```sql
USE BollywoodLens;
SHOW TABLES;
```

---

## 7. Load the Indian movies dataset

Ensure `data\indian movies.csv` is present (already included in the repository). Then run the loader:

```powershell
python scripts\load_movies.py --csv data\indian movies.csv --db-url mysql+pymysql://<user>:<password>@localhost/BollywoodLens
```

- The script cleans null values, normalises types, and upserts by `imdb_id`.
- Add `--chunk-size 500` (or larger) if you want to tune the insertion batches.

Check the row count afterward:
```sql
SELECT COUNT(*) FROM Movies;
```

---

## 8. Seed demo ratings (optional but great for demos)

Run the helper snippet to insert example ratings:

```powershell
python - <<'PY'
from sqlalchemy import create_engine, text
engine = create_engine("mysql+pymysql://<user>:<password>@localhost/BollywoodLens")
with engine.begin() as conn:
    conn.execute(text("""
        REPLACE INTO Ratings (user_id, movie_id, rating)
        VALUES (1, 28978, 9.5),
               (2, 22223, 9.0),
               (3, 29673, 8.8),
               (4, 7401, 9.2),
               (1, 22253, 9.6);
    """))
print("Inserted demo ratings.")
PY
```

---

## 9. Explore analysis queries

A curated set of advanced SQLs lives in `sql/analysis_queries.sql`:

```powershell
mysql -u <user> -p BollywoodLens < sql\analysis_queries.sql
```

Run them to gather insights like director leaderboards, rating distributions, and window-function examples.

---

## 10. Launch the Streamlit frontend

Ensure your virtual environment is active (Step 3), then:

```powershell
streamlit run app\streamlit_app.py
```

Features available in the UI:

- Live metrics summarising the database.
- Filterable movie search and genre analytics chart.
- A read-only SQL playground with CSV export.
- Tabs demonstrating the view, stored procedure, and trigger.

If prompted for a database URL, paste the same SQLAlchemy connection string used earlier.

---

## 11. Suggested SQL to try (for viva/demo)

- Top 10 Hindi hits:
  ```sql
  SELECT title, imdb_rating
  FROM Movies
  WHERE language = 'Hindi'
  ORDER BY imdb_rating DESC
  LIMIT 10;
  ```
- Stored procedure:
  ```sql
  CALL GetMoviesByGenre('Thriller');
  ```
- Trigger validation (should error when rating > 10):
  ```sql
  INSERT INTO Ratings (user_id, movie_id, rating) VALUES (1, 1, 11);
  ```

---

## 12. Preparing for GitHub push

1. Make sure the `.gitignore` file (included) excludes `.venv/`, `__pycache__/`, and other local artefacts.
2. Review your changes:
   ```powershell
   git status
   git diff
   ```
3. Commit with a clear message:
   ```powershell
   git add .
   git commit -m "Initial commit: BollywoodLens DBMS project"
   ```
4. Push to GitHub (replace remote name/URL as needed):
   ```powershell
   git remote add origin https://github.com/<your-org-or-username>/<your-repo-name>.git
   git push -u origin main
   ```

The repository now contains everything needed for collaborators or evaluators to recreate the environment end-to-end.

---

Need more automation? Consider wrapping the schema load + dataset import into a single shell script or Makefile. For production usage, add `.env.example` explaining required environment variables.
