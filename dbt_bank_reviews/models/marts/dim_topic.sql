WITH distinct_topics AS (
    SELECT DISTINCT topic_label
    FROM {{ source('staging_source', 'enriched_reviews') }}
    WHERE topic_label IS NOT NULL
)

SELECT
    MD5(topic_label)::text AS topic_id,
    topic_label
FROM distinct_topics