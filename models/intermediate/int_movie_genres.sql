SELECT
    movie_id,
    unnest(string_split(genres, '|')) AS genre
FROM {{ ref('stg_movies') }}