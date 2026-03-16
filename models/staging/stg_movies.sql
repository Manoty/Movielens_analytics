SELECT
    movieId        AS movie_id,
    title,
    genres
FROM {{ ref('movies') }}