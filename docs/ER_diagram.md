# BollywoodLens ER Diagram

```mermaid
erDiagram
    Movies ||--o{ Ratings : "is rated in"
    Users ||--o{ Ratings : "submits"

    Movies {
        int movie_id PK
        string imdb_id UK
        string title
        string genre
        string language
        int release_year
        int duration_minutes
        string director
        text actors
        decimal imdb_rating
        int votes
    }

    Users {
        int user_id PK
        string name
        string region
        string age_group
    }

    Ratings {
        int rating_id PK
        decimal rating
        datetime rated_at
    }
```

## Talking points for viva/demo

- **Movies** stores the master catalogue; `imdb_id` keeps it aligned with the public IMDb dataset.
- **Users** represents viewers who will eventually interact with the recommendation engine.
- **Ratings** resolves the many-to-many relationship and records each interaction, enabling analytics such as average rating per genre or per user cohort.
- The design supports future growth: sharding by language, adding `Directors` or `Actors` tables, and attaching ML pipelines without changing the core schema.
