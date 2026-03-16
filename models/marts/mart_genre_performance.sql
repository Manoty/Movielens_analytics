SELECT
    g.genre,
    COUNT(r.rating) AS total_ratings,
    AVG(r.rating) AS avg_rating
FROM {{ ref('int_movie_genres') }} g
JOIN {{ ref('fact_ratings') }} r
ON g.movie_id = r.movie_id
GROUP BY g.genre