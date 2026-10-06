WITH raw_dates AS (
    SELECT DISTINCT CAST(review_date AS DATE) AS review_date
    FROM {{ source('staging_source', 'enriched_reviews') }}
    WHERE review_date IS NOT NULL
)

SELECT
    CAST(TO_CHAR(review_date, 'YYYYMMDD') AS INT) AS date_id,
    review_date AS full_date,
    EXTRACT(YEAR FROM review_date) AS year,
    EXTRACT(MONTH FROM review_date) AS month,
    EXTRACT(QUARTER FROM review_date) AS quarter,
    TRIM(TO_CHAR(review_date, 'Day')) AS day
FROM raw_dates