SELECT
    movieId AS movie_id,
    imdbId AS imdb_id,
    tmdbId AS tmdb_id
FROM {{ ref('links') }}