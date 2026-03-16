SELECT
    m.movie_id,
    m.title,
    l.imdb_id,
    l.tmdb_id
FROM {{ ref('stg_movies') }} m
LEFT JOIN {{ ref('stg_links') }} l
ON m.movie_id = l.movie_id