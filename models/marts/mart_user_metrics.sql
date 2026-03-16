SELECT
    user_id,
    total_ratings,
    avg_rating,
    first_rating,
    last_rating
FROM {{ ref('int_user_activity') }}