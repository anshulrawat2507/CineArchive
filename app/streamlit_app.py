import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text, inspect
import os
from datetime import datetime
import re
from collections import defaultdict

# Database connection
DB_URL = os.getenv('BOLLYWOODLENS_DB_URL', 'mysql+pymysql://root:password@localhost/BollywoodLens')
engine = create_engine(DB_URL)

# Page config
st.set_page_config(
    page_title="BollywoodLens",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    .stApp {
        background: transparent;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9));
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        text-align: center;
        color: white;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        font-weight: 300;
        opacity: 0.95;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        text-align: center;
        color: white;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.4);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 1rem;
        font-weight: 400;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Movie Cards */
    .movie-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 5px solid #667eea;
    }
    
    .movie-card:hover {
        transform: translateX(10px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }
    
    .movie-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .movie-details {
        font-size: 0.95rem;
        color: #666;
        line-height: 1.6;
    }
    
    .imdb-badge {
        background: #f5c518;
        color: #000;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin-top: 0.5rem;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0,0,0,0.3);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stNumberInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stNumberInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
    }
    
    /* SQL Playground */
    .sql-playground {
        background: #1e293b;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        margin: 2rem 0;
    }
    
    .stTextArea textarea {
        background: #0f172a !important;
        color: #e2e8f0 !important;
        border: 2px solid #334155 !important;
        border-radius: 10px !important;
        font-family: 'Courier New', monospace !important;
        font-size: 1rem !important;
        padding: 1rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 15px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px 10px 0 0;
        padding: 1rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    section[data-testid="stSidebar"] .block-container {
        color: white;
    }
    
    /* DataFrame Styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 5px 20px rgba(0,0,0,0.15);
    }
    
    /* Success/Error Messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 10px;
        padding: 1rem;
        font-weight: 500;
    }
    
    /* Rating Stars */
    .rating-container {
        display: flex;
        gap: 0.5rem;
        align-items: center;
        margin: 1rem 0;
    }
    
    .star {
        font-size: 2rem;
        cursor: pointer;
        transition: transform 0.2s ease;
    }
    
    .star:hover {
        transform: scale(1.2);
    }
    
    /* Admin Badge */
    .admin-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin-left: 1rem;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
    }
    
    /* User Badge */
    .user-badge {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin-left: 1rem;
    }
    
    /* Query History */
    .query-history {
        background: #0f172a;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #334155;
    }
    
    .query-item {
        background: #1e293b;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #667eea;
        font-family: 'Courier New', monospace;
        color: #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Recommendation helpers
@st.cache_data(ttl=3600)
def get_table_columns(table_name):
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        return {column['name'] for column in columns}
    except Exception:
        return set()


def _split_tokens(value):
    if value is None:
        return []
    tokens = re.split(r'[|,]', str(value))
    return [token.strip().lower() for token in tokens if token and token.strip()]


def _normalize_genre_text(value):
    tokens = _split_tokens(value)
    seen = []
    for token in tokens:
        normalized = token.title()
        if normalized not in seen:
            seen.append(normalized)
    return ', '.join(seen)


def _build_token_set(row):
    tokens = set()
    for field in ["genre", "director", "actor_1", "actor_2", "actor_3", "language"]:
        tokens.update(_split_tokens(row.get(field)))
    year = row.get("release_year")
    if pd.notna(year):
        try:
            tokens.add(str(int(year)))
        except (TypeError, ValueError):
            tokens.add(str(year))
    return tokens


def _format_selector_label(row):
    year = row.get("release_year")
    if pd.isna(year):
        year_display = "N/A"
    else:
        try:
            year_display = str(int(year))
        except (TypeError, ValueError):
            year_display = str(year)
    language = row.get("language") or "Unknown"
    rating = row.get("imdb_rating")
    rating_display = f"{float(rating):.1f}" if pd.notna(rating) else "N/A"
    return f"{row.get('title', 'Unknown')} ({year_display}) • {language} • ⭐ {rating_display}"


def render_movie_card(row, extra_info=None):
    extra_info = extra_info or []
    year = row.get('release_year')
    if pd.isna(year):
        year_display = "N/A"
    else:
        try:
            year_display = str(int(year))
        except (TypeError, ValueError):
            year_display = str(year)
    language = row.get('language') or "Unknown"
    rating = row.get('imdb_rating')
    rating_display = f"{float(rating):.1f}" if pd.notna(rating) else "N/A"
    votes = row.get('votes')
    try:
        votes_display = f"{int(votes):,}"
    except (TypeError, ValueError):
        votes_display = "0"
    extras = []
    for label, value, fmt in extra_info:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            continue
        if fmt == "score":
            extras.append(f"<strong>{label}:</strong> {float(value):.2f}")
        elif fmt == "int":
            extras.append(f"<strong>{label}:</strong> {int(value)}")
        else:
            extras.append(f"<strong>{label}:</strong> {value}")
    extra_html = f"<br>{' | '.join(extras)}" if extras else ""
    st.markdown(f"""
    <div class="movie-card">
        <div class="movie-title">{row.get('title', 'Unknown')} ({year_display})</div>
        <div class="movie-details">
            <strong>Language:</strong> {language} | 
            <strong>Genre:</strong> {row.get('genre', 'N/A')}<br>
            <strong>Director:</strong> {row.get('director', 'N/A')}<br>
            <span class="imdb-badge">⭐ IMDb {rating_display}/10 ({votes_display} votes)</span>
            {extra_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_movie_metadata():
    desired_columns = [
        "movie_id",
        "title",
        "genre",
        "director",
        "actor_1",
        "actor_2",
        "actor_3",
        "language",
        "release_year",
        "imdb_rating",
        "votes",
        "duration",
    ]

    available_columns = get_table_columns("Movies")
    select_columns = [col for col in desired_columns if col in available_columns]

    if not select_columns:
        st.error("Movies table does not expose expected columns. Please verify the schema.")
        return pd.DataFrame(columns=desired_columns)

    select_clause = ", ".join(select_columns)

    with engine.connect() as conn:
        df = pd.read_sql(
            text(f"SELECT {select_clause} FROM Movies"),
            conn
        )

    missing_columns = [col for col in desired_columns if col not in df.columns]
    for column in missing_columns:
        df[column] = None

    # Ensure consistent column order
    df = df[desired_columns]
    if df.empty:
        df['token_set'] = []
        df['selector_label'] = []
        return df
    text_columns = ['genre', 'director', 'actor_1', 'actor_2', 'actor_3', 'language']
    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].fillna('')
    df['language'] = df['language'].replace('', 'Unknown')
    if 'genre' in df.columns:
        df['genre'] = df['genre'].apply(_normalize_genre_text)
    df['imdb_rating'] = pd.to_numeric(df['imdb_rating'], errors='coerce').fillna(0.0)
    df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)
    df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce').astype('Int64')
    df['token_set'] = df.apply(_build_token_set, axis=1)
    df['selector_label'] = df.apply(_format_selector_label, axis=1)
    return df


@st.cache_data(ttl=3600)
def load_genre_options():
    movie_df = load_movie_metadata()
    genres = set()
    if movie_df.empty:
        return []
    for value in movie_df['genre']:
        for token in _split_tokens(value):
            if token:
                genres.add(token.title())
    return sorted(genres)


def get_similar_movies(movie_df, base_movie_id, top_n=10):
    if movie_df.empty:
        return pd.DataFrame()
    base_row = movie_df.loc[movie_df['movie_id'] == base_movie_id]
    if base_row.empty:
        return pd.DataFrame()
    base_tokens = base_row.iloc[0]['token_set']
    if not base_tokens:
        return pd.DataFrame()

    def compute_jaccard(tokens):
        union = base_tokens | tokens
        if not union:
            return 0.0
        return len(base_tokens & tokens) / len(union)

    candidates = movie_df[movie_df['movie_id'] != base_movie_id].copy()
    candidates['similarity'] = candidates['token_set'].apply(compute_jaccard)
    candidates = candidates[candidates['similarity'] > 0]
    if candidates.empty:
        return pd.DataFrame()
    return candidates.sort_values('similarity', ascending=False).head(top_n)


def rank_popular_movies(movie_df, min_votes=1000, limit=10):
    if movie_df.empty:
        return pd.DataFrame()
    m = max(min_votes, 1)
    overall_avg = movie_df['imdb_rating'].mean()
    candidates = movie_df[movie_df['votes'] >= m].copy()
    if candidates.empty:
        candidates = movie_df.copy()
    candidates['popularity_score'] = (
        (candidates['votes'] / (candidates['votes'] + m)) * candidates['imdb_rating']
        + (m / (candidates['votes'] + m)) * overall_avg
    )
    return candidates.sort_values(['popularity_score', 'votes'], ascending=False).head(limit)


def recommend_movies_by_genre(movie_df, genre, min_rating=0.0, limit=10):
    if movie_df.empty or not genre:
        return pd.DataFrame()
    pattern = re.escape(genre)
    filtered = movie_df[movie_df['genre'].str.contains(pattern, case=False, na=False)].copy()
    filtered = filtered[filtered['imdb_rating'] >= float(min_rating)]
    if filtered.empty:
        return pd.DataFrame()
    return filtered.sort_values(['imdb_rating', 'votes'], ascending=False).head(limit)


@st.cache_data(ttl=600)
def fetch_user_rated_movies(user_id):
    with engine.connect() as conn:
        df = pd.read_sql(
            text("""SELECT m.movie_id, m.title, m.genre, m.language, m.release_year,
                         m.imdb_rating, m.votes, r.rating
                  FROM Ratings r
                  JOIN Movies m ON r.movie_id = m.movie_id
                  WHERE r.user_id = :user_id"""),
            conn,
            params={"user_id": user_id}
        )
    return df


def derive_user_preference_summary(ratings_df):
    if ratings_df.empty:
        return pd.DataFrame()
    aggregates = defaultdict(lambda: {"weighted": 0.0, "count": 0})
    for _, row in ratings_df.iterrows():
        rating_value = row.get('rating')
        if pd.isna(rating_value):
            continue
        for token in set(_split_tokens(row.get('genre', ''))):
            if not token:
                continue
            aggregates[token]['weighted'] += float(rating_value)
            aggregates[token]['count'] += 1
    summary_rows = []
    for genre_token, stats in aggregates.items():
        count = stats['count']
        if count == 0:
            continue
        avg_rating = stats['weighted'] / count
        summary_rows.append({
            "genre": genre_token.title(),
            "count": count,
            "avg_rating": avg_rating,
            "preference_score": avg_rating * 0.7 + count * 0.3
        })
    summary_df = pd.DataFrame(summary_rows)
    if summary_df.empty:
        return summary_df
    return summary_df.sort_values('preference_score', ascending=False)


def recommend_for_user(user_id, movie_df, preference_df, limit=10):
    if preference_df.empty:
        return pd.DataFrame()
    top_genres = preference_df.head(3)['genre'].str.lower().tolist()
    if not top_genres:
        return pd.DataFrame()
    with engine.connect() as conn:
        rated = conn.execute(
            text("SELECT movie_id FROM Ratings WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        rated_ids = {row[0] for row in rated}
    candidates = movie_df[~movie_df['movie_id'].isin(rated_ids)].copy()
    if candidates.empty:
        return pd.DataFrame()

    def compute_match_strength(genre_value):
        if not genre_value:
            return 0
        genre_text = str(genre_value).lower()
        return sum(1 for token in top_genres if token in genre_text)

    candidates['match_strength'] = candidates['genre'].apply(compute_match_strength)
    candidates = candidates[candidates['match_strength'] > 0]
    if candidates.empty:
        return pd.DataFrame()
    candidates['votes_normalized'] = candidates['votes'].apply(lambda v: min(v / 10000, 1.0))
    candidates['preference_score'] = (
        candidates['imdb_rating'] * 0.7
        + candidates['match_strength'] * 0.2
        + candidates['votes_normalized'] * 1.5
    )
    candidates = candidates.sort_values(
        ['preference_score', 'imdb_rating', 'votes'], ascending=False
    ).head(limit)
    return candidates.drop(columns=['votes_normalized'])

# Authentication functions
def login_user(engine, email, password):
    """Authenticate user using stored procedure"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("CALL AuthenticateUser(:email, :password)"),
                {"email": email, "password": password}
            )
            user = result.fetchone()
            conn.commit()
            
            if user:
                return {
                    'user_id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'is_admin': bool(user[3])
                }
    except Exception as e:
        st.error(f"Login error: {str(e)}")
    return None

def register_user(engine, name, email, password, region, age_group):
    """Register new user using stored procedure"""
    try:
        with engine.connect() as conn:
            conn.execute(
                text("CALL RegisterUser(:name, :email, :password, :region, :age_group)"),
                {
                    "name": name,
                    "email": email,
                    "password": password,
                    "region": region,
                    "age_group": age_group
                }
            )
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Registration error: {str(e)}")
        return False

def add_or_update_rating(engine, user_id, movie_id, rating):
    """Add or update movie rating using stored procedure"""
    try:
        with engine.connect() as conn:
            conn.execute(
                text("CALL AddOrUpdateRating(:user_id, :movie_id, :rating)"),
                {"user_id": user_id, "movie_id": movie_id, "rating": rating}
            )
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Rating error: {str(e)}")
        return False

def add_movie(engine, imdb_id, title, language, release_year, imdb_rating,
              votes, duration, genre, director, actor1, actor2, actor3, country):
    """Add new movie using stored procedure (admin only)."""

    # Combine actors into a single text field
    actors_text = ', '.join(filter(None, [actor1, actor2, actor3]))

    core_payload = {
        "imdb_id": imdb_id,
        "title": title,
        "genre": genre,
        "language": language,
        "release_year": release_year,
        "duration_minutes": duration,
        "director": director,
        "actors": actors_text,
        "imdb_rating": imdb_rating,
        "votes": votes,
    }

    try:
        with engine.connect() as conn:
            conn.execute(
                text("""CALL AddMovie(:imdb_id, :title, :genre, :language, :release_year,
                     :duration_minutes, :director, :actors, :imdb_rating, :votes)"""),
                core_payload
            )
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Add movie error: {str(e)}")
        return False

# Authentication page
def show_auth_page(engine):
    inject_custom_css()
    
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">🎬 BollywoodLens</div>
        <div class="hero-subtitle">Your Gateway to Indian Cinema</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Sign Up"])
    
    with tab1:
        st.markdown("### Welcome Back!")
        email = st.text_input("Email", key="login_email", placeholder="your.email@example.com")
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        
        if st.button("🚀 Login", key="login_btn"):
            if email and password:
                user = login_user(engine, email, password)
                if user:
                    st.session_state.user = user
                    st.session_state.is_admin = user['is_admin']
                    st.success(f"Welcome back, {user['name']}! 🎉")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
            else:
                st.warning("Please fill in all fields.")
    
    with tab2:
        st.markdown("### Join BollywoodLens Community!")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", key="reg_name", placeholder="John Doe")
            email = st.text_input("Email", key="reg_email", placeholder="john.doe@example.com")
            password = st.text_input("Password", type="password", key="reg_password", placeholder="Create a password")
        
        with col2:
            region = st.selectbox("Region", ["North", "South", "East", "West", "Central"], key="reg_region")
            age_group = st.selectbox("Age Group", ["18-25", "26-35", "36-45", "46-55", "55+"], key="reg_age")
        
        if st.button("✨ Create Account", key="register_btn"):
            if all([name, email, password, region, age_group]):
                if register_user(engine, name, email, password, region, age_group):
                    st.success("Account created successfully! Please sign in.")
                    st.balloons()
            else:
                st.warning("Please fill in all fields.")

# Home page
def show_home_page(engine):
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">🎬 BollywoodLens Dashboard</div>
        <div class="hero-subtitle">Explore 46,000+ Indian Movies</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    with engine.connect() as conn:
        total_movies = conn.execute(text("SELECT COUNT(*) FROM Movies")).scalar()
        total_ratings = conn.execute(text("SELECT COUNT(*) FROM Ratings")).scalar()
        avg_rating = conn.execute(text("SELECT AVG(imdb_rating) FROM Movies WHERE imdb_rating IS NOT NULL")).scalar()
        
        user_ratings = 0
        if st.session_state.user:
            user_ratings = conn.execute(
                text("SELECT COUNT(*) FROM Ratings WHERE user_id = :user_id"),
                {"user_id": st.session_state.user['user_id']}
            ).scalar()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Movies</div>
            <div class="metric-value">{total_movies:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Ratings</div>
            <div class="metric-value">{total_ratings:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Rating</div>
            <div class="metric-value">{avg_rating:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">My Ratings</div>
            <div class="metric-value">{user_ratings}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Top movies
    st.markdown("### 🌟 Top 10 Rated Movies")
    with engine.connect() as conn:
        df = pd.read_sql(
            text("""SELECT title, language, release_year, imdb_rating, votes, genre, director 
                    FROM Movies 
                    WHERE imdb_rating IS NOT NULL 
                    ORDER BY imdb_rating DESC, votes DESC 
                    LIMIT 10"""),
            conn
        )
    
    for idx, row in df.iterrows():
        st.markdown(f"""
        <div class="movie-card">
            <div class="movie-title">{idx + 1}. {row['title']}</div>
            <div class="movie-details">
                <strong>Language:</strong> {row['language']} | 
                <strong>Year:</strong> {row['release_year']} | 
                <strong>Genre:</strong> {row['genre']}<br>
                <strong>Director:</strong> {row['director']}<br>
                <span class="imdb-badge">⭐ IMDb {row['imdb_rating']}/10 ({row['votes']:,} votes)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Genre distribution
    st.markdown("### 📊 Movies by Genre (Top 10)")
    with engine.connect() as conn:
        genre_df = pd.read_sql(
            text("""SELECT genre, COUNT(*) as count 
                    FROM Movies 
                    WHERE genre IS NOT NULL AND genre != '' 
                    GROUP BY genre 
                    ORDER BY count DESC 
                    LIMIT 10"""),
            conn
        )
    st.bar_chart(genre_df.set_index('genre'))

# Search page
def show_search_page(engine):
    st.markdown("### 🔍 Advanced Movie Search")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        title_search = st.text_input("🎬 Movie Title", placeholder="Enter movie name...")
        language = st.selectbox("🗣️ Language", ["All", "Hindi", "Tamil", "Telugu", "Malayalam", "Kannada", "Bengali", "Marathi"])
    
    with col2:
        min_rating = st.slider("⭐ Minimum Rating", 0.0, 10.0, 0.0, 0.5)
        year_filter = st.selectbox("📅 Release Year", ["All"] + list(range(2024, 1950, -1)))
    
    with col3:
        genre_search = st.text_input("🎭 Genre", placeholder="e.g., Drama, Action...")
        director_search = st.text_input("🎥 Director", placeholder="Enter director name...")
    
    # Build query
    query = "SELECT * FROM Movies WHERE 1=1"
    params = {}
    
    if title_search:
        query += " AND title LIKE :title"
        params['title'] = f"%{title_search}%"
    
    if language != "All":
        query += " AND language = :language"
        params['language'] = language
    
    if min_rating > 0:
        query += " AND imdb_rating >= :min_rating"
        params['min_rating'] = min_rating
    
    if year_filter != "All":
        query += " AND release_year = :year"
        params['year'] = year_filter
    
    if genre_search:
        query += " AND genre LIKE :genre"
        params['genre'] = f"%{genre_search}%"
    
    if director_search:
        query += " AND director LIKE :director"
        params['director'] = f"%{director_search}%"
    
    query += " ORDER BY imdb_rating DESC LIMIT 50"
    
    if st.button("🚀 Search", key="search_btn"):
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params)

        st.markdown(f"### Found {len(df)} movies")

        if len(df) > 0:
            for idx, row in df.iterrows():
                title_value = row.get('title', 'Unknown')
                year_value = row.get('release_year')
                if year_value is None or (isinstance(year_value, float) and pd.isna(year_value)):
                    year_display = "N/A"
                else:
                    try:
                        year_display = str(int(float(year_value)))
                    except (TypeError, ValueError):
                        year_display = str(year_value)
                rating_value = row.get('imdb_rating')
                rating_display = f"{float(rating_value):.1f}" if pd.notna(rating_value) else "N/A"
                with st.expander(f"⭐ {title_value} ({year_display}) - {rating_display}/10"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        language_value = row.get('language', 'Unknown')
                        genre_value = row.get('genre', 'N/A')
                        director_value = row.get('director', 'N/A')
                        st.write(f"**Language:** {language_value if language_value else 'Unknown'}")
                        st.write(f"**Genre:** {genre_value if genre_value else 'N/A'}")
                        st.write(f"**Director:** {director_value if director_value else 'N/A'}")

                        actor_fields = ['actor_1', 'actor_2', 'actor_3']
                        cast_members = []
                        for field in actor_fields:
                            value = row.get(field)
                            if value is None or (isinstance(value, float) and pd.isna(value)):
                                continue
                            value_str = str(value).strip()
                            if value_str:
                                cast_members.append(value_str)
                        if not cast_members:
                            cast_members.append("N/A")
                        st.write(f"**Cast:** {', '.join(cast_members)}")

                        duration_value = row.get('duration')
                        if duration_value is None or (isinstance(duration_value, float) and pd.isna(duration_value)):
                            duration_display = "N/A"
                        else:
                            duration_display = f"{duration_value} min"
                        st.write(f"**Duration:** {duration_display}")

                        rating_value = row.get('imdb_rating')
                        rating_display = f"{float(rating_value):.1f}/10" if pd.notna(rating_value) else "N/A"
                        votes_value = row.get('votes', 0)
                        try:
                            votes_display = f"{int(votes_value):,}"
                        except (TypeError, ValueError):
                            votes_display = "0"
                        st.write(f"**IMDb:** {rating_display} ({votes_display} votes)")
                    
                    with col2:
                        if st.session_state.user:
                            rating = st.selectbox(
                                "Your Rating",
                                options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                                key=f"rating_{row['movie_id']}"
                            )
                            if st.button("💾 Save Rating", key=f"save_{row['movie_id']}"):
                                if rating > 0:
                                    if add_or_update_rating(engine, st.session_state.user['user_id'], row['movie_id'], rating):
                                        st.success("Rating saved!")
                                        st.balloons()
                                else:
                                    st.warning("Please select a rating")
        else:
            st.info("No movies found. Try adjusting your filters.")

# My Ratings page
def show_my_ratings_page(engine):
    st.markdown("### 🌟 My Movie Ratings")
    
    if not st.session_state.user:
        st.warning("Please login to view your ratings.")
        return
    
    with engine.connect() as conn:
        stats = conn.execute(
            text("""SELECT 
                    COUNT(*) as total_ratings,
                    AVG(rating) as avg_rating,
                    MAX(rating) as max_rating,
                    MIN(rating) as min_rating
                    FROM Ratings 
                    WHERE user_id = :user_id"""),
            {"user_id": st.session_state.user['user_id']}
        ).fetchone()
        total_ratings = stats[0] or 0
        average_rating = float(stats[1]) if stats[1] is not None else None
        highest_rating = stats[2]
        lowest_rating = stats[3]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Ratings", total_ratings)
        with col2:
            st.metric("Average Rating", f"{average_rating:.2f}" if average_rating is not None else "N/A")
        with col3:
            st.metric("Highest Rating", highest_rating if highest_rating is not None else "N/A")
        with col4:
            st.metric("Lowest Rating", lowest_rating if lowest_rating is not None else "N/A")
        
        st.markdown("---")
        ratings_columns = get_table_columns("Ratings")
        timestamp_column = None
        for candidate in ["rating_date", "rated_on", "created_at", "updated_at", "timestamp"]:
            if candidate in ratings_columns:
                timestamp_column = candidate
                break

        select_clause = "m.title, m.language, m.release_year, m.genre, m.imdb_rating, r.rating"
        if timestamp_column:
            select_clause += f", r.{timestamp_column} AS rating_timestamp"
        else:
            select_clause += ", NULL AS rating_timestamp"

        order_clause = f"ORDER BY r.{timestamp_column} DESC" if timestamp_column else "ORDER BY r.rating DESC"

        query = text(f"""SELECT {select_clause}
                        FROM Ratings r
                        JOIN Movies m ON r.movie_id = m.movie_id
                        WHERE r.user_id = :user_id
                        {order_clause}""")

        df = pd.read_sql(
            query,
            conn,
            params={"user_id": st.session_state.user['user_id']}
        )
        
        if len(df) > 0:
            if 'rating_timestamp' in df.columns:
                df = df.rename(columns={'rating_timestamp': 'Rated On'})
                try:
                    df['Rated On'] = pd.to_datetime(df['Rated On'])
                    df['Rated On'] = df['Rated On'].dt.strftime('%Y-%m-%d %H:%M')
                except Exception:
                    df['Rated On'] = df['Rated On'].astype(str)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("You haven't rated any movies yet. Start exploring!")

# Recommendations hub
def show_recommendations_page(engine):
    """Aggregate the different recommendation strategies into a single page."""

    movie_df = load_movie_metadata()
    if movie_df.empty:
        st.info("No movies available yet. Come back after adding a few titles.")
        return

    st.markdown("### 🎯 Smart Recommendations Hub")
    st.markdown("Explore movies through similarity, popularity, genres, and personalised picks.")

    st.divider()

    # --- Content-based similarity section
    st.markdown("#### 🔍 Because you liked...")
    selectable = (
        movie_df[['selector_label', 'movie_id']]
        .dropna(subset=['selector_label'])
        .drop_duplicates(subset=['movie_id'])
        .sort_values('selector_label')
    )
    if selectable.empty:
        st.info("Need at least one movie with descriptive metadata to show look-alikes.")
    else:
        default_index = min(5, len(selectable) - 1)
        chosen_label = st.selectbox(
            "Pick a movie to find similar ones",
            selectable['selector_label'].tolist(),
            index=default_index if default_index >= 0 else 0,
        )
        chosen_row = selectable.loc[selectable['selector_label'] == chosen_label]
        base_movie_id = int(chosen_row.iloc[0]['movie_id'])
        top_n = st.slider("How many matches?", 3, 20, 8)
        similar_df = get_similar_movies(movie_df, base_movie_id, top_n)
        if similar_df.empty:
            st.info("No close matches discovered. Try another title.")
        else:
            for _, row in similar_df.iterrows():
                render_movie_card(row, extra_info=[("Similarity", row.get('similarity'), "score")])

    st.divider()

    # --- Popularity based section
    st.markdown("#### 📈 Crowd Favorites")
    col_pop_1, col_pop_2 = st.columns(2)
    with col_pop_1:
        vote_floor = st.slider("Minimum IMDb votes", 0, 20000, 1000, 100)
    with col_pop_2:
        popular_limit = st.slider("How many titles?", 5, 30, 10)
    popular_df = rank_popular_movies(movie_df, min_votes=max(vote_floor, 1), limit=popular_limit)
    if popular_df.empty:
        st.info("Not enough vote data yet to rank popularity.")
    else:
        for _, row in popular_df.iterrows():
            render_movie_card(row, extra_info=[("Popularity Score", row.get('popularity_score'), "score")])

    st.divider()

    # --- Genre exploration section
    st.markdown("#### 🎭 Genre Explorer")
    genre_options = load_genre_options()
    if not genre_options:
        st.info("Genre metadata missing. Update a few movies with genres to unlock this section.")
    else:
        col_genre_1, col_genre_2 = st.columns([2, 1])
        with col_genre_1:
            selected_genre = st.selectbox("Choose a genre", genre_options)
        with col_genre_2:
            min_genre_rating = st.slider("IMDb rating floor", 0.0, 10.0, 7.0, 0.1)
        genre_limit = st.slider("Genre picks", 5, 20, 8, key="genre_limit_slider")
        genre_df = recommend_movies_by_genre(movie_df, selected_genre, min_rating=min_genre_rating, limit=genre_limit)
        if genre_df.empty:
            st.info("No titles meet those filters right now. Try relaxing the rating floor.")
        else:
            for _, row in genre_df.iterrows():
                render_movie_card(row)

    st.divider()

    # --- Personalised picks section
    st.markdown("#### ❤️ Tailored For You")
    if not st.session_state.user:
        st.info("Login to unlock personalised insights and recommendations.")
        return

    user_id = st.session_state.user['user_id']
    user_ratings_df = fetch_user_rated_movies(user_id)
    if user_ratings_df.empty:
        st.info("Rate a few movies to train your personal tastes.")
        return

    preference_df = derive_user_preference_summary(user_ratings_df)
    if preference_df.empty:
        st.info("We need a broader taste profile. Try rating a few more genres.")
        return

    with st.expander("See your top genres", expanded=True):
        st.dataframe(preference_df.head(10), use_container_width=True)

    personal_limit = st.slider("Personalised picks", 3, 15, 6, key="personal_limit_slider")
    personalised_df = recommend_for_user(user_id, movie_df, preference_df, limit=personal_limit)
    if personalised_df.empty:
        st.info("All matching titles are already rated by you. Explore other sections for fresh ideas!")
    else:
        for _, row in personalised_df.iterrows():
            render_movie_card(
                row,
                extra_info=[
                    ("Preference Score", row.get('preference_score'), "score"),
                    ("Match Strength", row.get('match_strength'), "int"),
                ],
            )

# SQL Playground
def show_sql_playground(engine):
    st.markdown("""
    <div class="sql-playground">
        <h2 style="color: white; margin-bottom: 1rem;">💻 SQL Playground</h2>
        <p style="color: #94a3b8; margin-bottom: 2rem;">Run read-only SQL queries on our database</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Query examples
    st.markdown("### 📚 Query Examples")
    examples = {
        "🎬 Top 10 Movies": "SELECT title, imdb_rating, votes FROM Movies ORDER BY imdb_rating DESC, votes DESC LIMIT 10;",
        "🗣️ Movies by Language": "SELECT language, COUNT(*) as count FROM Movies GROUP BY language ORDER BY count DESC;",
        "📅 Movies by Year": "SELECT release_year, COUNT(*) as count FROM Movies WHERE release_year >= 2020 GROUP BY release_year ORDER BY release_year DESC;",
        "⭐ High Rated (>8.5)": "SELECT title, imdb_rating, genre FROM Movies WHERE imdb_rating > 8.5 ORDER BY imdb_rating DESC;",
        "🎭 Genre Distribution": "SELECT genre, COUNT(*) as movies, AVG(imdb_rating) as avg_rating FROM Movies WHERE genre IS NOT NULL GROUP BY genre ORDER BY movies DESC LIMIT 15;",
        "🎥 Top Directors": "SELECT director, COUNT(*) as movies, AVG(imdb_rating) as avg_rating FROM Movies WHERE director IS NOT NULL GROUP BY director HAVING movies >= 5 ORDER BY avg_rating DESC LIMIT 20;",
        "📊 Rating Distribution": "SELECT FLOOR(imdb_rating) as rating_range, COUNT(*) as count FROM Movies WHERE imdb_rating IS NOT NULL GROUP BY FLOOR(imdb_rating) ORDER BY rating_range;"
    }
    
    cols = st.columns(3)
    for idx, (name, query) in enumerate(examples.items()):
        with cols[idx % 3]:
            if st.button(name, key=f"example_{idx}"):
                st.session_state.current_query = query
    
    # Query input
    query = st.text_area(
        "Enter your SQL query:",
        value=st.session_state.get('current_query', ''),
        height=150,
        placeholder="SELECT * FROM Movies LIMIT 10;"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        execute = st.button("🚀 Execute Query", key="execute_sql")
    
    if execute and query:
        # Security: Allow only SELECT, SHOW, DESCRIBE, CALL, EXPLAIN
        if not any(query.strip().upper().startswith(cmd) for cmd in ['SELECT', 'SHOW', 'DESCRIBE', 'DESC', 'CALL', 'EXPLAIN']):
            st.error("⚠️ Only SELECT, SHOW, DESCRIBE, CALL, and EXPLAIN queries are allowed.")
        else:
            try:
                with engine.connect() as conn:
                    df = pd.read_sql(text(query), conn)
                
                st.success(f"✅ Query executed successfully! Found {len(df)} rows.")
                st.dataframe(df, use_container_width=True)
                
                # Add to history
                if len(st.session_state.query_history) >= 10:
                    st.session_state.query_history.pop(0)
                st.session_state.query_history.append({
                    'query': query,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'rows': len(df)
                })
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv"
                )
                
            except Exception as e:
                st.error(f"❌ Query Error: {str(e)}")
    
    # Query history
    if st.session_state.query_history:
        st.markdown("### 📜 Query History (Last 10)")
        for idx, item in enumerate(reversed(st.session_state.query_history)):
            st.markdown(f"""
            <div class="query-item">
                <small style="color: #94a3b8;">{item['timestamp']} • {item['rows']} rows</small><br>
                {item['query']}
            </div>
            """, unsafe_allow_html=True)

# Admin Panel
def show_admin_panel(engine):
    if not st.session_state.is_admin:
        st.error("⚠️ Access Denied: Admin privileges required.")
        return
    
    st.markdown("### 🔧 Admin Panel - Add New Movie")
    
    col1, col2 = st.columns(2)
    
    with col1:
        imdb_id = st.text_input("IMDb ID", placeholder="tt1234567")
        title = st.text_input("Movie Title", placeholder="Enter movie title")
        language = st.selectbox("Language", ["Hindi", "Tamil", "Telugu", "Malayalam", "Kannada", "Bengali", "Marathi", "English"])
        release_year = st.number_input("Release Year", min_value=1900, max_value=2025, value=2024)
        imdb_rating = st.number_input("IMDb Rating", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
        votes = st.number_input("Votes", min_value=0, value=1000)
    
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, value=120)
        genre = st.text_input("Genre", placeholder="Drama, Action")
        director = st.text_input("Director", placeholder="Director name")
        actor1 = st.text_input("Actor 1", placeholder="Lead actor")
        actor2 = st.text_input("Actor 2", placeholder="Supporting actor")
        actor3 = st.text_input("Actor 3", placeholder="Supporting actor")
        country = st.text_input("Country", placeholder="India")
    
    if st.button("➕ Add Movie", key="add_movie_btn"):
        if all([imdb_id, title, language]):
            if add_movie(engine, imdb_id, title, language, release_year, imdb_rating,
                        votes, duration, genre, director, actor1, actor2, actor3, country):
                st.success("✅ Movie added successfully!")
                st.balloons()
        else:
            st.warning("Please fill in at least IMDb ID, Title, and Language.")

# DBMS Concepts Demo
def show_dbms_concepts(engine):
    st.markdown("### 📚 DBMS Concepts Demonstration")
    
    tab1, tab2, tab3 = st.tabs(["📊 Views", "⚙️ Stored Procedures", "🔔 Triggers"])
    
    with tab1:
        st.markdown("#### View: TopRatedMovies")
        st.info("A VIEW is a virtual table based on a SELECT query. It provides a way to present data from one or more tables in a specific format.")
        
        rating_threshold = st.slider("Rating Threshold", 0.0, 10.0, 8.5, 0.5)
        
        with engine.connect() as conn:
            # Create or replace view
            conn.execute(text(f"""
                CREATE OR REPLACE VIEW TopRatedMovies AS
                SELECT title, language, release_year, imdb_rating, votes
                FROM Movies
                WHERE imdb_rating >= {rating_threshold}
                ORDER BY imdb_rating DESC, votes DESC
            """))
            conn.commit()
            
            # Query the view
            df = pd.read_sql(text("SELECT * FROM TopRatedMovies LIMIT 20"), conn)
            
        st.dataframe(df, use_container_width=True)
        st.code(f"""CREATE OR REPLACE VIEW TopRatedMovies AS
SELECT title, language, release_year, imdb_rating, votes
FROM Movies
WHERE imdb_rating >= {rating_threshold}
ORDER BY imdb_rating DESC, votes DESC;""", language="sql")
    
    with tab2:
        st.markdown("#### Stored Procedure: GetMoviesByGenre")
        st.info("A STORED PROCEDURE is a prepared SQL code that can be saved and reused. It can accept parameters and execute complex operations.")
        
        genre_input = st.text_input("Enter Genre", value="Drama", key="genre_proc")
        
        if st.button("Execute Procedure", key="exec_proc"):
            with engine.connect() as conn:
                df = pd.read_sql(
                    text("CALL GetMoviesByGenre(:genre)"),
                    conn,
                    params={"genre": genre_input}
                )
                
            st.dataframe(df, use_container_width=True)
        
        st.code("""CREATE PROCEDURE GetMoviesByGenre(IN genre_name VARCHAR(100))
BEGIN
    SELECT title, release_year, imdb_rating, director
    FROM Movies
    WHERE genre LIKE CONCAT('%', genre_name, '%')
    ORDER BY imdb_rating DESC
    LIMIT 25;
END;""", language="sql")
    
    with tab3:
        st.markdown("#### Trigger: BeforeRatingInsert")
        st.info("A TRIGGER is a database object that automatically executes in response to certain events (INSERT, UPDATE, DELETE).")
        
        st.markdown("**Test the rating validation trigger:**")
        test_rating = st.number_input("Enter a rating to test (try 11.0!)", 0.0, 15.0, 8.5, 0.5, key="test_trigger")
        
        if st.button("Test Trigger", key="test_trig"):
            if test_rating < 0 or test_rating > 10:
                st.error(f"❌ Trigger would reject this! Rating must be between 0 and 10. You entered: {test_rating}")
            else:
                st.success(f"✅ Trigger would accept this rating: {test_rating}")
        
        st.code("""CREATE TRIGGER BeforeRatingInsert
BEFORE INSERT ON Ratings
FOR EACH ROW
BEGIN
    IF NEW.rating < 0 OR NEW.rating > 10 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Rating must be between 0 and 10';
    END IF;
END;""", language="sql")

# Main app
def main():
    inject_custom_css()
    
    # Check if user is logged in
    if not st.session_state.user:
        show_auth_page(engine)
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem 0;">
            <h2 style="color: white;">👤 {st.session_state.user['name']}</h2>
            <p style="color: #e2e8f0;">{st.session_state.user['email']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.is_admin:
            st.markdown('<span class="admin-badge">👑 ADMIN</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="user-badge">👤 USER</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        menu_options = [
            "🏠 Home",
            "🔍 Search",
            "🌟 My Ratings",
            "🤖 Recommendations",
            "💻 SQL Playground",
            "📚 DBMS Concepts"
        ]
        if st.session_state.is_admin:
            menu_options.append("🔧 Admin Panel")
        
        choice = st.radio("Navigation", menu_options)
        
        st.markdown("---")
        
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.session_state.is_admin = False
            st.rerun()
    
    # Main content
    if choice == "🏠 Home":
        show_home_page(engine)
    elif choice == "🔍 Search":
        show_search_page(engine)
    elif choice == "🌟 My Ratings":
        show_my_ratings_page(engine)
    elif choice == "🤖 Recommendations":
        show_recommendations_page(engine)
    elif choice == "💻 SQL Playground":
        show_sql_playground(engine)
    elif choice == "📚 DBMS Concepts":
        show_dbms_concepts(engine)
    elif choice == "🔧 Admin Panel":
        show_admin_panel(engine)

if __name__ == "__main__":
    main()
