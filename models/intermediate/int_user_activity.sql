SELECT
    user_id,
    COUNT(*) AS total_ratings,
    AVG(rating) AS avg_rating,
    MIN(rating_timestamp) AS first_rating,
    MAX(rating_timestamp) AS last_rating
FROM {{ ref('stg_ratings') }}
GROUP BY user_id