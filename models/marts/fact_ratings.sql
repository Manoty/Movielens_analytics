SELECT
    user_id,
    movie_id,
    rating,
    rating_timestamp
FROM {{ ref('stg_ratings') }}