WITH raw_branches AS (
    SELECT DISTINCT 
        bank_name,
        COALESCE(location, 'Adresse inconnue') AS location,
        city
    FROM {{ source('staging_source', 'enriched_reviews') }}
)

SELECT
    MD5(bank_name || location)::text AS branch_id,
    MD5(bank_name)::text AS bank_id,

    CASE 
        WHEN location = 'Adresse inconnue' THEN bank_name || ' - Agence Digitale / Inconnue'
        ELSE bank_name || ' - Agence ' || location 
    END AS branch_name,
    location,
    city
FROM raw_branches