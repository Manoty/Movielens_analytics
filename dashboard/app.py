import streamlit as st
import duckdb
import plotly.express as px

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="MovieLens Analytics Dashboard",
    layout="wide"
)

st.title("Movielens Analytics Dashboard")




# -------------------------
# DB CONNECTION
# -------------------------
con = duckdb.connect("dev.duckdb")

# -------------------------
# KPI CARDS
# -------------------------

kpi_query = """
SELECT
    COUNT(DISTINCT movie_id) AS total_movies,
    COUNT(*) AS total_ratings,
    COUNT(DISTINCT user_id) AS total_users,
    AVG(rating) AS avg_rating
FROM fact_ratings
"""

kpi_df = con.execute(kpi_query).fetchdf()

col1, col2, col3, col4 = st.columns(4)

col1.metric("🎬 Total Movies", kpi_df["total_movies"][0])
col2.metric("⭐ Total Ratings", kpi_df["total_ratings"][0])
col3.metric("👤 Total Users", kpi_df["total_users"][0])
col4.metric("📊 Avg Rating", round(kpi_df["avg_rating"][0], 2))

# -------------------------
# GENRE FILTER
# -------------------------
genre_list_query = """
SELECT DISTINCT genre
FROM mart_genre_performance
ORDER BY genre
"""

genres = con.execute(genre_list_query).fetchdf()["genre"].tolist()

selected_genre = st.sidebar.selectbox(
    "Filter by Genre",
    ["All"] + genres
)

# -------------------------
# TOP RATED MOVIES
# -------------------------
st.subheader("Top Rated Movies")

st.markdown(
    "_Shows the highest-rated movies based on average user ratings, filtered to include only movies with a significant number of ratings to ensure reliability._"
)
query_top_movies = """
SELECT
    d.title,
    AVG(f.rating) AS avg_rating,
    COUNT(*) AS rating_count
FROM fact_ratings f
JOIN dim_movies d
    ON f.movie_id = d.movie_id
GROUP BY d.title
HAVING COUNT(*) > 50
ORDER BY avg_rating DESC
LIMIT 10
"""

df_top_movies = con.execute(query_top_movies).fetchdf()

fig1 = px.bar(
    df_top_movies,
    x="avg_rating",
    y="title",
    orientation="h",
    title="Top Rated Movies",
    template="plotly_dark"
)

st.plotly_chart(fig1, use_container_width=True)

# -------------------------
# GENRE PERFORMANCE
# -------------------------
st.subheader("Average Rating by Genre")

st.markdown(
    "_Displays how different genres perform in terms of average user ratings, helping identify which types of content are most appreciated._"
)

query_genres = """
SELECT
    genre,
    avg_rating,
    total_ratings
FROM mart_genre_performance
ORDER BY avg_rating DESC
"""

df_genres = con.execute(query_genres).fetchdf()

fig2 = px.bar(
    df_genres,
    x="genre",
    y="avg_rating",
    title="Average Rating by Genre",
    template="plotly_dark"
)

st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# MOST ACTIVE USERS
# -------------------------
st.subheader("Most Active Users")

st.markdown(
    "_Shows the highest-rated movies based on average user ratings, filtered to include only movies with a significant number of ratings to ensure reliability._"
)

query_users = """
SELECT
    user_id,
    total_ratings
FROM mart_user_metrics
ORDER BY total_ratings DESC
LIMIT 10
"""

df_users = con.execute(query_users).fetchdf()

fig3 = px.bar(
    df_users,
    x="user_id",
    y="total_ratings",
    title="Most Active Users",
    template="plotly_dark"
)

st.plotly_chart(fig3, use_container_width=True)

# -------------------------
# RATING DISTRIBUTION
# -------------------------
st.subheader("Rating Distribution")

st.markdown(
    "_Shows the highest-rated movies based on average user ratings, filtered to include only movies with a significant number of ratings to ensure reliability._"
)

query_rating_dist = """
SELECT
    rating,
    COUNT(*) AS total
FROM fact_ratings
GROUP BY rating
ORDER BY rating
"""

df_rating_dist = con.execute(query_rating_dist).fetchdf()

fig4 = px.bar(
    df_rating_dist,
    x="rating",
    y="total",
    title="Distribution of Movie Ratings",
    template="plotly_dark"
)

st.plotly_chart(fig4, use_container_width=True)

# -------------------------
# RATINGS OVER TIME
# -------------------------
st.subheader("Ratings Over Time")

st.markdown(
    "_Shows the highest-rated movies based on average user ratings, filtered to include only movies with a significant number of ratings to ensure reliability._"
)

query_ratings_time = """
SELECT
    DATE(rating_timestamp) AS rating_date,
    COUNT(*) AS total_ratings
FROM fact_ratings
GROUP BY rating_date
ORDER BY rating_date
"""

df_ratings_time = con.execute(query_ratings_time).fetchdf()

fig5 = px.line(
    df_ratings_time,
    x="rating_date",
    y="total_ratings",
    title="Ratings Activity Over Time",
    template="plotly_dark"
)

st.plotly_chart(fig5, use_container_width=True)

# -------------------------
# MOST POPULAR GENRES
# -------------------------
st.subheader("Most Popular Genres")

st.markdown(
    "_Shows the highest-rated movies based on average user ratings, filtered to include only movies with a significant number of ratings to ensure reliability._"
)

query_genre_popularity = """
SELECT
    genre,
    total_ratings
FROM mart_genre_performance
ORDER BY total_ratings DESC
LIMIT 10
"""

df_genre_popularity = con.execute(query_genre_popularity).fetchdf()

fig6 = px.bar(
    df_genre_popularity,
    x="genre",
    y="total_ratings",
    title="Most Popular Genres",
    template="plotly_dark"
)

st.plotly_chart(fig6, use_container_width=True)

# -------------------------
# TOP MOVIES BY GENRE
# -------------------------
st.subheader("Top Movies by Selected Genre")

st.markdown(
    "_Shows the highest-rated movies based on average user ratings, filtered to include only movies with a significant number of ratings to ensure reliability._"
)

if selected_genre == "All":
    query_genre_movies = """
    SELECT
        d.title,
        AVG(f.rating) AS avg_rating,
        COUNT(*) AS rating_count
    FROM fact_ratings f
    JOIN dim_movies d
        ON f.movie_id = d.movie_id
    GROUP BY d.title
    HAVING COUNT(*) > 50
    ORDER BY avg_rating DESC
    LIMIT 15
    """
else:
    query_genre_movies = f"""
    SELECT
        d.title,
        AVG(f.rating) AS avg_rating,
        COUNT(*) AS rating_count
    FROM fact_ratings f
    JOIN dim_movies d
        ON f.movie_id = d.movie_id
    JOIN int_movie_genres g
        ON d.movie_id = g.movie_id
    WHERE g.genre = '{selected_genre}'
    GROUP BY d.title
    HAVING COUNT(*) > 20
    ORDER BY avg_rating DESC
    LIMIT 15
    """

df_genre_movies = con.execute(query_genre_movies).fetchdf()

fig7 = px.bar(
    df_genre_movies,
    x="avg_rating",
    y="title",
    orientation="h",
    title=f"Top Movies - {selected_genre}",
    template="plotly_dark"
)

st.plotly_chart(fig7, use_container_width=True)

# -------------------------
# -------------------------
# NETFLIX-STYLE MOVIE EXPLORER
# -------------------------

st.subheader("🎬 Movie Explorer")

st.markdown(
    "_Shows the highest-rated movies based on average user ratings, filtered to include only movies with a significant number of ratings to ensure reliability._"
)

# Get movie list
movie_list_query = """
SELECT DISTINCT title
FROM dim_movies
ORDER BY title
LIMIT 1000
"""

movie_list = con.execute(movie_list_query).fetchdf()["title"].tolist()

selected_movie = st.selectbox(
    "Select a movie",
    movie_list
)

# -------------------------
# MOVIE DETAILS
# -------------------------

if selected_movie:

    movie_details_query = """
    SELECT
        d.title,
        AVG(f.rating) AS avg_rating,
        COUNT(f.rating) AS total_ratings
    FROM dim_movies d
    LEFT JOIN fact_ratings f
        ON d.movie_id = f.movie_id
    WHERE d.title = ?
    GROUP BY d.title
    """

    df_details = con.execute(movie_details_query, [selected_movie]).fetchdf()

    col1, col2, col3 = st.columns(3)

    if not df_details.empty:
        col1.metric("🎬 Movie", df_details["title"][0])
        col2.metric("⭐ Avg Rating", round(df_details["avg_rating"][0], 2) if df_details["avg_rating"][0] else "N/A")
        col3.metric("🔥 Total Ratings", int(df_details["total_ratings"][0]))

# -------------------------
# RATING DISTRIBUTION
# -------------------------

    rating_dist_query = """
    SELECT
        rating,
        COUNT(*) AS total
    FROM fact_ratings f
    JOIN dim_movies d
        ON f.movie_id = d.movie_id
    WHERE d.title = ?
    GROUP BY rating
    ORDER BY rating
    """

    df_rating_dist = con.execute(rating_dist_query, [selected_movie]).fetchdf()

    if not df_rating_dist.empty:
        fig_movie_dist = px.bar(
            df_rating_dist,
            x="rating",
            y="total",
            title="Rating Distribution",
            template="plotly_dark"
        )
        st.plotly_chart(fig_movie_dist, use_container_width=True)
    else:
        st.info("No rating data available for this movie.")

# -------------------------
# GENRE BREAKDOWN
# -------------------------

    genre_query = """
    SELECT
        g.genre,
        COUNT(*) AS total
    FROM int_movie_genres g
    JOIN dim_movies d
        ON g.movie_id = d.movie_id
    WHERE d.title = ?
    GROUP BY g.genre
    """

    df_genre = con.execute(genre_query, [selected_movie]).fetchdf()

    if not df_genre.empty:
        fig_genre = px.pie(
            df_genre,
            names="genre",
            values="total",
            title="Genre Breakdown",
            template="plotly_dark"
        )
        st.plotly_chart(fig_genre, use_container_width=True)

# -------------------------
# SIMILAR MOVIES
# -------------------------

    st.subheader("🔥 Similar Popular Movies")

    similar_movies_query = """
    SELECT
        d.title,
        AVG(f.rating) AS avg_rating,
        COUNT(*) AS rating_count
    FROM fact_ratings f
    JOIN dim_movies d
        ON f.movie_id = d.movie_id
    JOIN int_movie_genres g
        ON d.movie_id = g.movie_id
    WHERE g.genre IN (
        SELECT genre
        FROM int_movie_genres g2
        JOIN dim_movies d2
            ON g2.movie_id = d2.movie_id
        WHERE d2.title = ?
    )
    GROUP BY d.title
    HAVING COUNT(*) > 50
    ORDER BY avg_rating DESC
    LIMIT 10
    """

    df_similar = con.execute(similar_movies_query, [selected_movie]).fetchdf()

    st.dataframe(df_similar)
    
    
st.markdown(
    """
    <style>
    /* Page background */
    .main {
        background-color: #0D0D0D;
        color: #FAFAFA;
        font-family: sans-serif;
    }

    /* Sidebar background */
    .stSidebar {
        background-color: #121212;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #FAFAFA;
    }

    /* KPI cards and metrics */
    .stMetric {
        background-color: rgba(29, 185, 84, 0.1); /* subtle green overlay */
        border-radius: 8px;
        padding: 10px;
        color: #FAFAFA;
    }

    /* Buttons and highlights (simulate primaryColor) */
    .stButton>button {
        background-color: #1DB954;
        color: #FFFFFF;
        border-radius: 8px;
    }

    /* Streamlit charts (optional: text inside charts) */
    .element-container {
        color: #FAFAFA;
    }
    </style>
    """,
    unsafe_allow_html=True
)
