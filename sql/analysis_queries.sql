-- Advanced analysis queries for BollywoodLens
-- Run after loading data to explore deeper insights.

USE BollywoodLens;

-- 1. Recent decade highlights (2015 onwards)
SELECT
    release_year,
    title,
    imdb_rating,
    genre
FROM Movies
WHERE release_year >= 2015 AND imdb_rating IS NOT NULL
ORDER BY imdb_rating DESC, votes DESC
LIMIT 20;

-- 2. Best director averages (min 5 titles)
SELECT
    director,
    COUNT(*) AS movie_count,
    ROUND(AVG(imdb_rating), 2) AS avg_rating,
    SUM(votes) AS total_votes
FROM Movies
WHERE director IS NOT NULL AND director <> '' AND imdb_rating IS NOT NULL
GROUP BY director
HAVING COUNT(*) >= 5
ORDER BY avg_rating DESC, total_votes DESC
LIMIT 15;

-- 3. Genre popularity trend over time
SELECT
    release_year,
    genre,
    COUNT(*) AS genre_titles
FROM Movies
WHERE genre IS NOT NULL AND genre <> ''
  AND release_year BETWEEN 2000 AND YEAR(CURDATE())
GROUP BY release_year, genre
ORDER BY release_year DESC, genre_titles DESC;

-- 4. Longest movies per language
SELECT
    language,
    title,
    duration_minutes
FROM (
    SELECT
        language,
        title,
        duration_minutes,
        ROW_NUMBER() OVER (PARTITION BY language ORDER BY duration_minutes DESC) AS lang_rank
    FROM Movies
    WHERE language IS NOT NULL AND duration_minutes IS NOT NULL
) ranked
WHERE lang_rank <= 3
ORDER BY language, duration_minutes DESC;

-- 5. IMDb rating distribution buckets
SELECT
    CONCAT(FLOOR(imdb_rating), ' - ', FLOOR(imdb_rating) + 1) AS rating_bucket,
    COUNT(*) AS movies_in_bucket
FROM Movies
WHERE imdb_rating IS NOT NULL
GROUP BY rating_bucket
ORDER BY rating_bucket;
