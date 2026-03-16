SELECT
    userId AS user_id,
    movieId AS movie_id,
    tag,
    to_timestamp(timestamp) AS tag_timestamp
FROM {{ ref('tags') }}