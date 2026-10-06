WITH sentiments AS (
    SELECT 'positive' AS sentiment_label, 1 AS sentiment_score
    UNION ALL
    SELECT 'neutral' AS sentiment_label, 0 AS sentiment_score
    UNION ALL
    SELECT 'negative' AS sentiment_label, -1 AS sentiment_score
)

SELECT 
    MD5(sentiment_label)::text AS sentiment_id,
    sentiment_label,
    sentiment_score
FROM sentiments