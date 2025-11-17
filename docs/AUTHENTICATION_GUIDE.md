# Authentication & Rating Features - User Guide

## Overview
BollywoodLens now includes user authentication, a rating system, and admin capabilities for managing movie data.

## Features Added

### 1. User Authentication
- **Sign Up**: Create a new account with name, email, password, region, and age group
- **Login**: Access your account using email and password
- **Session Management**: Stay logged in during your session
- **User Roles**: Regular users and administrators

### 2. Movie Rating System
- **Rate Movies**: Give any movie a rating from 0 to 10
- **View Your Ratings**: See all movies you've rated with timestamps
- **Update Ratings**: Change your rating for any movie at any time
- **Unique Ratings**: One rating per user per movie (enforced by database constraint)

### 3. Admin Panel (Admin Users Only)
- **Add New Movies**: Insert new movies with complete details:
  - IMDb ID (must be unique)
  - Title, Genre, Language
  - Release Year, Duration
  - Director, Actors
  - IMDb Rating and Votes
- **Validation**: Prevents duplicate IMDb IDs

## Demo Credentials

### Admin Account
- **Email**: admin@bollywoodlens.com
- **Password**: admin123
- **Capabilities**: Can rate movies + add new movies

### Creating New Users
Use the "Sign Up" tab to create regular user accounts.

## Database Changes

### New Columns in `Users` Table
```sql
email VARCHAR(255) UNIQUE
password_hash VARCHAR(255)
is_admin BOOLEAN DEFAULT FALSE
last_login TIMESTAMP NULL
```

### New Stored Procedures
1. **RegisterUser** - Create new user accounts
2. **AuthenticateUser** - Validate login credentials
3. **AddOrUpdateRating** - Save/update user ratings
4. **GetUserRatings** - Retrieve all ratings for a user
5. **AddMovie** - Insert new movies (admin only)

### New Indexes (Performance Optimization)
- `idx_users_email` on Users(email)
- `idx_ratings_user` on Ratings(user_id)
- `idx_ratings_movie` on Ratings(movie_id)
- `idx_movies_year` on Movies(release_year)
- `idx_movies_rating` on Movies(imdb_rating)
- `idx_movies_language` on Movies(language)

### Unique Constraint
- `unique_user_movie` on Ratings(user_id, movie_id)

## Usage Workflow

### For Regular Users
1. Sign up or log in
2. Browse movies using search filters
3. Rate movies by selecting a rating and clicking save (💾)
4. View your rating history in "My Ratings" section
5. Explore database statistics and charts

### For Administrators
1. Log in with admin credentials
2. Access the "Admin Panel - Add New Movie" section
3. Fill in movie details
4. Click "➕ Add Movie"
5. All regular user features are also available

## Security Notes

**⚠️ Important for Production:**
- Current implementation uses plain-text password storage for demo purposes
- In production, replace with bcrypt/scrypt hashing
- Add password strength requirements
- Implement rate limiting on login attempts
- Use HTTPS for secure transmission
- Add email verification
- Implement password reset functionality

## Setup Instructions

### 1. Apply Authentication Schema
```bash
cd E:\5thsem\PBL\DBMS\CineArchive
python scripts/setup_auth.py
```

### 2. Run the Application
```bash
streamlit run app/streamlit_app.py
```

### 3. Set Database URL (if needed)
```bash
$env:BOLLYWOODLENS_DB_URL='mysql+pymysql://root:password@localhost/BollywoodLens'
```

## Troubleshooting

### "Invalid email or password"
- Check that you're using the correct credentials
- Ensure the email is registered (use Sign Up first)

### "Email already registered"
- This email is already in use
- Try logging in instead, or use a different email

### "Movie with this IMDb ID already exists"
- Each IMDb ID must be unique
- Check if the movie is already in the database

### Duplicate ratings error
- Run `scripts/setup_auth.py` to clean up duplicates
- The unique constraint prevents future duplicates

## Future Enhancements
- Password reset via email
- User profiles with preferences
- Movie recommendations based on ratings
- Social features (follow users, share ratings)
- Watchlist functionality
- Advanced search filters
- Movie details page with cast/crew
