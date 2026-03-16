import streamlit as st
import duckdb
import plotly.express as px

st.title("MovieLens Analytics Dashboard")

# connect to dbt DuckDB database
con = duckdb.connect("dev.duckdb")

# Top Rated Movies
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

fig = px.bar(
    df_top_movies,
    x="avg_rating",
    y="title",
    orientation="h",
    title="Top Rated Movies"
)

st.plotly_chart(fig)

# Genre Performance
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
    title="Average Rating by Genre"
)

st.plotly_chart(fig2)

# Most Active Users
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
    title="Most Active Users"
)

st.plotly_chart(fig3)