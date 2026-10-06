WITH enriched_data AS (
    SELECT * FROM {{ source('staging_source', 'enriched_reviews') }}
)

SELECT
    -- Génération d'un ID unique garanti 
    MD5(clean_text || bank_name || review_date::text || ROW_NUMBER() OVER(ORDER BY review_date))::text AS review_id,
    -- Foreign Keys 
    MD5(bank_name)::text AS bank_id,
    MD5(bank_name || COALESCE(location, 'Adresse inconnue'))::text AS branch_id,
    MD5(sentiment)::text AS sentiment_id,
    MD5(topic_label)::text AS topic_id,
    MD5(language)::text AS language_id,
    CAST(TO_CHAR(review_date, 'YYYYMMDD') AS INT) AS date_id,
    
    -- Mesures 
    rating,
    clean_text 
FROM enriched_data