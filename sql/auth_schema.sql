-- Authentication and authorization enhancements for BollywoodLens
-- Run this AFTER bollywoodlens_schema.sql

USE BollywoodLens;

-- Add authentication columns to Users table
ALTER TABLE Users
ADD COLUMN email VARCHAR(255) UNIQUE,
ADD COLUMN password_hash VARCHAR(255),
ADD COLUMN is_admin BOOLEAN DEFAULT FALSE,
ADD COLUMN last_login TIMESTAMP NULL;

-- Create unique constraint on user ratings (one rating per user per movie)
ALTER TABLE Ratings
ADD CONSTRAINT unique_user_movie UNIQUE (user_id, movie_id);

-- Create admin user (password: admin123)
-- In production, use proper password hashing with bcrypt/scrypt
UPDATE Users 
SET email = 'admin@bollywoodlens.com',
    password_hash = 'admin123',  -- Simplified for demo; use bcrypt in production
    is_admin = TRUE
WHERE name = 'Aarav Sharma';

-- Authentication stored procedures
DELIMITER //

DROP PROCEDURE IF EXISTS RegisterUser //
CREATE PROCEDURE RegisterUser(
    IN p_name VARCHAR(100),
    IN p_email VARCHAR(255),
    IN p_password VARCHAR(255),
    IN p_region VARCHAR(100),
    IN p_age_group VARCHAR(50)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Registration failed';
    END;
    
    START TRANSACTION;
    
    -- Check if email already exists
    IF EXISTS (SELECT 1 FROM Users WHERE email = p_email) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Email already registered';
    END IF;
    
    INSERT INTO Users (name, email, password_hash, region, age_group, is_admin)
    VALUES (p_name, p_email, p_password, p_region, p_age_group, FALSE);
    
    COMMIT;
    SELECT LAST_INSERT_ID() AS user_id;
END //

DROP PROCEDURE IF EXISTS AuthenticateUser //
CREATE PROCEDURE AuthenticateUser(
    IN p_email VARCHAR(255),
    IN p_password VARCHAR(255)
)
BEGIN
    DECLARE v_user_id INT;
    DECLARE v_is_admin BOOLEAN;
    
    -- Find user with matching credentials
    SELECT user_id, is_admin INTO v_user_id, v_is_admin
    FROM Users
    WHERE email = p_email AND password_hash = p_password;
    
    IF v_user_id IS NOT NULL THEN
        -- Update last login
        UPDATE Users SET last_login = CURRENT_TIMESTAMP WHERE user_id = v_user_id;
        
        -- Return user info
        SELECT user_id, name, email, is_admin, region, age_group
        FROM Users
        WHERE user_id = v_user_id;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid email or password';
    END IF;
END //

DROP PROCEDURE IF EXISTS AddOrUpdateRating //
CREATE PROCEDURE AddOrUpdateRating(
    IN p_user_id INT,
    IN p_movie_id INT,
    IN p_rating DECIMAL(3,1)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Rating operation failed';
    END;
    
    START TRANSACTION;
    
    -- Insert or update rating
    INSERT INTO Ratings (user_id, movie_id, rating)
    VALUES (p_user_id, p_movie_id, p_rating)
    ON DUPLICATE KEY UPDATE 
        rating = p_rating,
        rated_at = CURRENT_TIMESTAMP;
    
    COMMIT;
    SELECT 'Rating saved successfully' AS message;
END //

DROP PROCEDURE IF EXISTS GetUserRatings //
CREATE PROCEDURE GetUserRatings(IN p_user_id INT)
BEGIN
    SELECT 
        r.rating_id,
        m.title,
        m.genre,
        m.release_year,
        m.imdb_rating,
        r.rating AS user_rating,
        r.rated_at
    FROM Ratings r
    JOIN Movies m ON r.movie_id = m.movie_id
    WHERE r.user_id = p_user_id
    ORDER BY r.rated_at DESC;
END //

DROP PROCEDURE IF EXISTS AddMovie //
CREATE PROCEDURE AddMovie(
    IN p_imdb_id VARCHAR(12),
    IN p_title VARCHAR(255),
    IN p_genre VARCHAR(255),
    IN p_language VARCHAR(100),
    IN p_release_year INT,
    IN p_duration_minutes INT,
    IN p_director VARCHAR(255),
    IN p_actors TEXT,
    IN p_imdb_rating DECIMAL(3,1),
    IN p_votes INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Failed to add movie';
    END;
    
    START TRANSACTION;
    
    -- Check if IMDb ID already exists
    IF EXISTS (SELECT 1 FROM Movies WHERE imdb_id = p_imdb_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Movie with this IMDb ID already exists';
    END IF;
    
    INSERT INTO Movies (
        imdb_id, title, genre, language, release_year, 
        duration_minutes, director, actors, imdb_rating, votes
    )
    VALUES (
        p_imdb_id, p_title, p_genre, p_language, p_release_year,
        p_duration_minutes, p_director, p_actors, p_imdb_rating, p_votes
    );
    
    COMMIT;
    SELECT LAST_INSERT_ID() AS movie_id, 'Movie added successfully' AS message;
END //

DELIMITER ;

-- Create indexes for performance
CREATE INDEX idx_users_email ON Users(email);
CREATE INDEX idx_ratings_user ON Ratings(user_id);
CREATE INDEX idx_ratings_movie ON Ratings(movie_id);
CREATE INDEX idx_movies_year ON Movies(release_year);
CREATE INDEX idx_movies_rating ON Movies(imdb_rating);
CREATE INDEX idx_movies_language ON Movies(language);
