WITH distinct_languages AS (
    SELECT DISTINCT language
    FROM {{ source('staging_source', 'enriched_reviews') }}
    WHERE language IS NOT NULL
)

SELECT 
    MD5(language)::text AS language_id,
    language AS language_code,
    
    CASE 
        -- principal languages (Contexte Marocain & International standard)
        WHEN language = 'fr' THEN 'Français'
        WHEN language = 'ar' THEN 'Arabe / Darija'
        WHEN language = 'en' THEN 'Anglais'
        WHEN language = 'es' THEN 'Espagnol'
        
        -- Common European languages
        WHEN language = 'de' THEN 'Allemand'
        WHEN language = 'it' THEN 'Italien'
        WHEN language = 'pt' THEN 'Portugais'
        WHEN language = 'nl' THEN 'Néerlandais'
        WHEN language = 'nl' THEN 'Néerlandais'
        WHEN language = 'tr' THEN 'Turc'
        WHEN language = 'ru' THEN 'Russe'
        WHEN language = 'pl' THEN 'Polonais'
        WHEN language = 'ro' THEN 'Roumain'
        WHEN language = 'sv' THEN 'Suédois'
        WHEN language = 'da' THEN 'Danois'
        WHEN language = 'ca' THEN 'Catalan'
        
        -- Asian languages & Middle East
        WHEN language = 'ja' THEN 'Japonais'
        WHEN language = 'zh-cn' THEN 'Chinois (Simplifié)'
        WHEN language = 'zh-tw' THEN 'Chinois (Traditionnel)'
        WHEN language = 'ko' THEN 'Coréen'
        WHEN language = 'he' THEN 'Hébreu'
        
        ELSE 'Autre (' || language || ')' 
    END AS language_name

FROM distinct_languages