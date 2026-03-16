import streamlit as st
import duckdb
import plotly.express as px

st.set_page_config(
page_title="MovieLens Analytics Dashboard",
layout="wide"
)

st.title("MovieLens Analytics Dashboard")

# Connect to DuckDB (same DB dbt uses)

con = duckdb.connect("dev.duckdb")

# -------------------------------

# GENRE FILTER

# -------------------------------

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

# -------------------------------

# TOP RATED MOVIES

# -------------------------------

st.subheader("Top Rated Movies")

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
title="Top Rated Movies"
)

st.plotly_chart(fig1, use_container_width=True)

# -------------------------------

# GENRE PERFORMANCE

# -------------------------------

st.subheader("Average Rating by Genre")

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

st.plotly_chart(fig2, use_container_width=True)

# -------------------------------

# MOST ACTIVE USERS

# -------------------------------

st.subheader("Most Active Users")

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

st.plotly_chart(fig3, use_container_width=True)

# -------------------------------

# RATING DISTRIBUTION

# -------------------------------

st.subheader("Rating Distribution")

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
title="Distribution of Movie Ratings"
)

st.plotly_chart(fig4, use_container_width=True)

# -------------------------------

# RATINGS OVER TIME

# -------------------------------

st.subheader("Ratings Over Time")

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
title="Ratings Activity Over Time"
)

st.plotly_chart(fig5, use_container_width=True)

# -------------------------------

# MOST POPULAR GENRES

# -------------------------------

st.subheader("Most Popular Genres")

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
title="Most Popular Genres"
)

st.plotly_chart(fig6, use_container_width=True)

# -------------------------------

# TOP MOVIES BY SELECTED GENRE

# -------------------------------

st.subheader("Top Movies by Selected Genre")

if selected_genre == "All":

```
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
```

else:

```
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
```

df_genre_movies = con.execute(query_genre_movies).fetchdf()

fig7 = px.bar(
df_genre_movies,
x="avg_rating",
y="title",
orientation="h",
title=f"Top Movies - {selected_genre}"
)

st.plotly_chart(fig7, use_container_width=True)

# -------------------------------

# MOVIE SEARCH

# -------------------------------

st.subheader("Movie Rating Lookup")

movie_name = st.text_input("Search movie title")

if movie_name:

```
query_movie = f"""
SELECT
    d.title,
    AVG(f.rating) AS avg_rating,
    COUNT(*) AS rating_count
FROM fact_ratings f
JOIN dim_movies d
ON f.movie_id = d.movie_id
WHERE LOWER(d.title) LIKE LOWER('%{movie_name}%')
GROUP BY d.title
ORDER BY avg_rating DESC
LIMIT 20
"""

df_movie = con.execute(query_movie).fetchdf()

st.dataframe(df_movie)
```
