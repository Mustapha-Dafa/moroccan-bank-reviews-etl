{{ config(
    schema='staging'
) }}

WITH raw_data AS (
    SELECT * FROM {{ source('staging_source', 'reviews_raw') }}
),

-- 1. Normalisation des noms de banques
standardized_banks AS (
    SELECT 
        *,
        -- Convertit en minuscules, remplace "banque" par "bank", puis met la 1ère lettre de chaque mot en majuscule
        INITCAP(REPLACE(LOWER(bank_name), 'banque', 'bank')) AS standardized_bank_name
    FROM raw_data
),

-- 2. Suppression des doublons
deduplicated AS (
    -- DISTINCT supprime les lignes 100% identiques. 
    -- (On pourrait aussi utiliser ROW_NUMBER() si on veut dédoublonner uniquement sur le texte et la date)
    SELECT DISTINCT * FROM standardized_banks
)

-- 3. Application des filtres finaux et gestion des valeurs manquantes
SELECT
    city,
    standardized_bank_name AS bank_name,
    TRIM(location) AS location, -- Retire les espaces au début et à la fin
    
    -- Normalisation du texte : minuscules + suppression de la ponctuation
    REGEXP_REPLACE(LOWER(review_text), '[^\w\s]', '', 'g') AS clean_text,
    
    -- Gestion des valeurs manquantes (COALESCE)
    COALESCE(rating, 0) AS rating,
    
    -- Cast explicite pour s'assurer que la date est au bon format
    CAST(review_date AS DATE) AS review_date

FROM deduplicated
-- Sécurité supplémentaire : exclure les lignes sans texte ou ne contenant que des espaces
WHERE review_text IS NOT NULL 
  AND TRIM(review_text) != ''