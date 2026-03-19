import streamlit as st
import duckdb
import subprocess
import plotly.express as px
import os

if not os.path.exists("dev.duckdb"):
    subprocess.run(["dbt", "run"], cwd="movielens_analytics")

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="MovieLens Analytics Dashboard",
    layout="wide"
)

# -------------------------
# NETFLIX-STYLE CSS  (moved to top so it loads before any UI renders)
# -------------------------
st.markdown("""
<style>

/* ── Page background ── */
[data-testid="stAppViewContainer"] {
    background-color: #141414;
    color: #FFFFFF;
    font-family: 'Helvetica Neue', Helvetica, sans-serif;
}

/* ── Top header bar ── */
[data-testid="stHeader"] {
    background-color: #141414;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #1B1B1B;
    color: #FFFFFF;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* ── Headings ── */
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
    font-weight: 700;
    text-shadow: 1px 1px 3px #B81D24;
}

/* ── KPI metric cards ── */
[data-testid="stMetric"] {
    background-color: rgba(229, 9, 20, 0.15);
    border-radius: 8px;
    padding: 10px;
    color: #FFFFFF;
}

[data-testid="stMetric"] * {
    color: #FFFFFF !important;
}

/* ── Metric value (the big number) ── */
[data-testid="stMetricValue"] {
    color: #E50914 !important;
    font-weight: 700;
}

/* ── Buttons ── */
[data-testid="stButton"] > button {
    background-color: #E50914;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}

[data-testid="stButton"] > button:hover {
    background-color: #B81D24;
    color: #FFFFFF;
}

/* ── General text ── */
p, span, div, label {
    color: #FFFFFF;
}

/* ── Links ── */
a, a:hover {
    color: #E50914 !important;
}

/* ── Selectbox / dropdowns ── */
div[data-baseweb="select"] > div {
    background-color: #2B2B2B !important;
    border: 1px solid #E50914 !important;
    border-radius: 6px !important;
    color: #FFFFFF !important;
}

div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    color: #FFFFFF !important;
    background-color: #2B2B2B !important;
}

/* ── Dropdown open popup list ── */
ul[data-baseweb="menu"] {
    background-color: #2B2B2B !important;
}

li[role="option"] {
    background-color: #2B2B2B !important;
    color: #FFFFFF !important;
}

li[role="option"]:hover {
    background-color: #E50914 !important;
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 Movielens Analytics Dashboard")

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
# GENRE FILTER (sidebar)
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
    "_The highest-rated movies based on average user ratings. Only movies with more than 50 ratings are included to ensure statistical reliability._"
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
    "_How different genres perform in terms of average user ratings — useful for spotting which content types are most appreciated._"
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
    "_The top 10 users who have submitted the most ratings on the platform._"
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
    "_Breakdown of how ratings are spread across the 0.5–5 star scale, showing the overall rating behaviour of users._"
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
    "_Volume of ratings submitted per day, revealing platform activity trends and peak engagement periods._"
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
    "_Genres ranked by total number of ratings received — a measure of audience reach rather than quality._"
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
# TOP MOVIES BY GENRE  (uses sidebar genre filter)
# -------------------------
st.subheader("Top Movies by Selected Genre")
st.markdown(
    "_Top-rated movies filtered by your selected genre from the sidebar. Switch genre to explore different categories._"
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
    df_genre_movies = con.execute(query_genre_movies).fetchdf()
else:
    # ✅ Fixed: parameterized query to prevent SQL injection
    query_genre_movies = """
    SELECT
        d.title,
        AVG(f.rating) AS avg_rating,
        COUNT(*) AS rating_count
    FROM fact_ratings f
    JOIN dim_movies d
        ON f.movie_id = d.movie_id
    JOIN int_movie_genres g
        ON d.movie_id = g.movie_id
    WHERE g.genre = ?
    GROUP BY d.title
    HAVING COUNT(*) > 20
    ORDER BY avg_rating DESC
    LIMIT 15
    """
    df_genre_movies = con.execute(query_genre_movies, [selected_genre]).fetchdf()

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
# MOVIE EXPLORER
# -------------------------
st.subheader("🎬 Movie Explorer")
st.markdown(
    "_Search for any movie to see its average rating, total ratings, genre breakdown, and a list of similar titles._"
)

movie_list_query = """
SELECT DISTINCT title
FROM dim_movies
ORDER BY title
LIMIT 1000
"""

movie_list = con.execute(movie_list_query).fetchdf()["title"].tolist()

selected_movie = st.selectbox("Select a movie", movie_list)

if selected_movie:

    # ── Movie Details ──
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
        avg = df_details["avg_rating"][0]
        # ✅ Fixed: safe None check before rounding
        avg_display = round(float(avg), 2) if avg is not None else "N/A"

        col1.metric("🎬 Movie", df_details["title"][0])
        col2.metric("⭐ Avg Rating", avg_display)
        col3.metric("🔥 Total Ratings", int(df_details["total_ratings"][0]))

    # ── Rating Distribution ──
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

    df_movie_rating_dist = con.execute(rating_dist_query, [selected_movie]).fetchdf()

    if not df_movie_rating_dist.empty:
        fig_movie_dist = px.bar(
            df_movie_rating_dist,
            x="rating",
            y="total",
            title=f"Rating Distribution — {selected_movie}",
            template="plotly_dark"
        )
        st.plotly_chart(fig_movie_dist, use_container_width=True)
    else:
        st.info("No rating data available for this movie.")

    # ── Genre Breakdown ──
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
            title=f"Genre Breakdown — {selected_movie}",
            template="plotly_dark"
        )
        st.plotly_chart(fig_genre, use_container_width=True)

    # ── Similar Movies ──
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
    AND d.title != ?
    GROUP BY d.title
    HAVING COUNT(*) > 50
    ORDER BY avg_rating DESC
    LIMIT 10
    """

    # ✅ Fixed: pass selected_movie twice (used in two ? placeholders)
    df_similar = con.execute(similar_movies_query, [selected_movie, selected_movie]).fetchdf()

    if not df_similar.empty:
        st.dataframe(df_similar)
    else:
        st.info("No similar movies found.")
        
        
st.markdown("""
---
<div style="text-align: center; color: #555555; font-size: 13px; padding: 20px 0;">
    Built by <span style="color: #E50914; font-weight: 600;">Kev</span> &nbsp;|&nbsp; 
    MovieLens Analytics Dashboard &nbsp;|&nbsp; Powered by Streamlit & DuckDB
</div>
""", unsafe_allow_html=True)        

