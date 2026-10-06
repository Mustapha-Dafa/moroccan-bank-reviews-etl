WITH distinct_banks AS (
    SELECT DISTINCT bank_name
    FROM {{ source('staging_source', 'enriched_reviews') }}
    WHERE bank_name IS NOT NULL
)

SELECT
    MD5(bank_name)::text AS bank_id,
    bank_name
FROM distinct_banks