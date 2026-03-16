SELECT
    userId AS user_id,
    movieId AS movie_id,
    rating,
    to_timestamp(timestamp) AS rating_timestamp
FROM {{ ref('ratings') }}