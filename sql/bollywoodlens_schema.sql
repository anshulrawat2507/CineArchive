-- BollywoodLens database schema and DBMS artifacts
-- Run this script in a MySQL 8.x session.

DROP DATABASE IF EXISTS BollywoodLens;
CREATE DATABASE BollywoodLens CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE BollywoodLens;

-- Core tables ---------------------------------------------------------------
CREATE TABLE Movies (
    movie_id INT AUTO_INCREMENT PRIMARY KEY,
    imdb_id VARCHAR(12) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    genre VARCHAR(255),
    language VARCHAR(100),
    release_year INT,
    duration_minutes INT,
    director VARCHAR(255),
    actors TEXT,
    imdb_rating DECIMAL(3,1),
    votes INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (imdb_rating IS NULL OR (imdb_rating >= 0 AND imdb_rating <= 10))
);

CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    age_group VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Ratings (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    rating DECIMAL(3,1) NOT NULL,
    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ratings_user FOREIGN KEY (user_id)
        REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_ratings_movie FOREIGN KEY (movie_id)
        REFERENCES Movies(movie_id) ON DELETE CASCADE,
    CHECK (rating >= 0 AND rating <= 10)
);

-- Sample seed data for Users table to support demo operations --------------
INSERT INTO Users (name, region, age_group) VALUES
('Aarav Sharma', 'Delhi', '18-24'),
('Zoya Patel', 'Mumbai', '25-34'),
('Kabir Khan', 'Bengaluru', '25-34'),
('Meera Iyer', 'Chennai', '35-44');

-- Derived objects -----------------------------------------------------------
DROP VIEW IF EXISTS TopRatedMovies;
CREATE VIEW TopRatedMovies AS
SELECT
    title,
    genre,
    language,
    release_year,
    imdb_rating
FROM Movies
WHERE imdb_rating IS NOT NULL AND imdb_rating >= 8.0;

DELIMITER //
DROP PROCEDURE IF EXISTS GetMoviesByGenre //
CREATE PROCEDURE GetMoviesByGenre(IN genre_query VARCHAR(100))
BEGIN
    SELECT
        title,
        release_year,
        imdb_rating,
        language
    FROM Movies
    WHERE genre LIKE CONCAT('%', genre_query, '%')
    ORDER BY imdb_rating DESC, release_year DESC;
END //

DROP TRIGGER IF EXISTS BeforeRatingInsert //
CREATE TRIGGER BeforeRatingInsert
BEFORE INSERT ON Ratings
FOR EACH ROW
BEGIN
    IF NEW.rating < 0 OR NEW.rating > 10 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid rating value (must be between 0 and 10)';
    END IF;
END //
DELIMITER ;

-- Demonstration queries ----------------------------------------------------
-- Top 10 Hindi movies by IMDb rating
SELECT title, imdb_rating
FROM Movies
WHERE language = 'Hindi'
ORDER BY imdb_rating DESC
LIMIT 10;

-- Average IMDb rating per genre
SELECT genre, AVG(imdb_rating) AS avg_rating
FROM Movies
WHERE imdb_rating IS NOT NULL AND genre IS NOT NULL
GROUP BY genre
ORDER BY avg_rating DESC;

-- Movies released per year
SELECT release_year, COUNT(*) AS movie_count
FROM Movies
GROUP BY release_year
ORDER BY release_year DESC;
