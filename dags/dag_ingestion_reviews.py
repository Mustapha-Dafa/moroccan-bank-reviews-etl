from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator 
from airflow.providers.standard.operators.python import PythonOperator   
from datetime import datetime, timedelta
from airflow.providers.http.operators.http import HttpOperator
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
import joblib
from sqlalchemy import create_engine
from langdetect import detect


def upload_raw_reviews():
    df_raw = pd.read_csv("/opt/airflow/data/reviews.csv")
    df_raw =df_raw[["city","bank_name", "review_date", "location", "rating","review_text"]]

    # PostgreSQL Connection
    conn1 = psycopg2.connect(
        dbname=os.getenv("DBNAME"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        host="host.docker.internal",
        port=os.getenv("PORT")
    )

    with conn1.cursor() as cur:
        # Create the table if it does not exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS staging.reviews_raw (
                city TEXT,
                bank_name TEXT,
                location TEXT,
                review_text TEXT,
                rating FLOAT,
                review_date DATE
            );
        """)
        conn1.commit()

        # Insert the data
        execute_values(
            cur,
            "INSERT INTO staging.reviews_raw (city ,bank_name, review_date, location, rating,review_text ) VALUES %s",
            df_raw.values.tolist()
        )
        conn1.commit()

    conn1.close()
    print("✅ Table staging.reviews_raw créée et données insérées.")



def enrich_reviews():

    # 1. PostgreSQL Connection
    print("Connexion à la base de données...")

    engine = create_engine(
        f'postgresql+psycopg2://'
        f'{os.getenv("USER")}:{os.getenv("PASSWORD")}'
        f'@host.docker.internal/{os.getenv("DBNAME")}'
    )

    # 2. Extraction of cleaned data
    df = pd.read_sql_table(
        'clean_reviews',
        con=engine,
        schema='staging'
    )

    if df.empty:
        print("Aucune donnée à traiter.")
        return

    # 3. Language detection
    def detect_language(text):
        try:
            return detect(text)
        except:
            return "unknown"

    df['language'] = df['clean_text'].apply(detect_language)

    # 4. Sentiment classification
    def classify_sentiment(rating):
        if pd.isna(rating):
            return "neutral"
        elif rating >= 4:
            return "positive"
        elif rating == 3:
            return "neutral"
        else:
            return "negative"

    df['sentiment'] = df['rating'].apply(classify_sentiment)

    # 5. Topic classification using LDA

    df_nlp = df.dropna(subset=['clean_text']).copy()

    df_nlp = df_nlp[
        df_nlp['clean_text'].astype(str).str.strip() != 'nan'
    ]

    df_nlp = df_nlp[
        df_nlp['clean_text'].astype(str).str.strip() != ''
    ]

    if df_nlp.empty:

        df['topic_label'] = 'Non classifié (Texte manquant)'

    else:

        # Path to ML models
        model_path = '/opt/airflow/ml_models'

        vectorizer = joblib.load(
            os.path.join(
                model_path,
                'vectorizer_v1.joblib'
            )
        )

        lda_model = joblib.load(
            os.path.join(
                model_path,
                'lda_model_v1.joblib'
            )
        )

        # Vectorization
        tf_matrix_new = vectorizer.transform(
            df_nlp['clean_text']
        )

        # LDA inference
        lda_matrix_new = lda_model.transform(
            tf_matrix_new
        )

        # Dominant Topic
        df_nlp['dominant_topic_id'] = (
            lda_matrix_new.argmax(axis=1)
        )

        # Correspondance topic → label
        topic_labels = {
            0: "Accueil et Relation Client",
            1: "Support à Distance & Gestion de Compte",
            2: "Expérience Globale en Agence",
            3: "Qualité du Personnel"
        }

        df_nlp['topic_label'] = (
            df_nlp['dominant_topic_id']
            .map(topic_labels)
        )

        # Reintegration into the original dataframe
        df = df.merge(
            df_nlp[['topic_label']],
            left_index=True,
            right_index=True,
            how='left'
        )

        df['topic_label'] = df['topic_label'].fillna(
            'Non classifié (Texte manquant)'
        )

    # 6. saving
    df.to_sql(
        'enriched_reviews',
        con=engine,
        schema='staging',
        if_exists='replace',
        index=False
    )

    print("Pipeline NLP terminé avec succès.")



default_args = {
    'owner': 'airflow',
    'start_date': datetime(2026, 9, 1),
    'retries': 1,
    'retry_delay': timedelta(seconds=10)
    
}

with DAG(
    'daily_reviews_pipeline',
    default_args=default_args,
    schedule='@daily',
    catchup=False,
    description='Pipeline quotidien de scraping, NLP et modélisation',
    tags=['nlp', 'dbt', 'pipeline'],
) as dag:

    
    # task 1 - Scrape reviews 
    scrape_reviews = HttpOperator(
        task_id="scrape_reviews",
        http_conn_id="scraper_api",
        endpoint="scrape",
        method="POST",
        headers={
            "Content-Type": "application/json"
        },
        data="{}",
        log_response=True,
    )

    # task 2 - Upload to PostgreSQL
    upload_data = PythonOperator(
        task_id='upload_reviews',
        python_callable=upload_raw_reviews
    )

    # task 3 - Cleaning with DBT
    dbt_clean = BashOperator(
        task_id='dbt_clean',
        bash_command='cd /opt/airflow/dbt_bank_reviews && /home/airflow/.local/bin/dbt run --select staging --profiles-dir .'
    )

    # # task 4 - NLP Enrichment
    enrich_nlp = PythonOperator(
        task_id='enrich_reviews',
        python_callable=enrich_reviews
    )

    # # task 5 - Build fact and dimension tables with dbt.
    dbt_build_dwh = BashOperator(
        task_id='dbt_build_dwh',
        bash_command='cd /opt/airflow/dbt_bank_reviews && dbt run --select marts --profiles-dir .'
    )

    # Dependances
    scrape_reviews >> upload_data >> dbt_clean >> enrich_nlp >> dbt_build_dwh 
