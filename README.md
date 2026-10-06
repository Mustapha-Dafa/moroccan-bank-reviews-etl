# 🏦 Moroccan Bank Reviews Data Warehouse

> **An automated, end-to-end ETL pipeline to extract, transform, and analyze (via NLP) Google Maps reviews for Moroccan bank branches in the Rabat-Salé-Kénitra region.**

The goal of this project is to understand customer satisfaction in the banking sector by centralizing public reviews. We use a **FastAPI** microservice to orchestrate Selenium scraping, apply Machine Learning models (language detection, topic modeling, and sentiment analysis) via Apache Airflow, and store the processed data in a structured Data Warehouse. The data is then ready to be plugged into any Business Intelligence (BI) tool of your choice.

---

## 🛠️ Technology Stack

- **Data Scraping & APIs**: Python, Selenium, FastAPI
- **Orchestration**: Apache Airflow
- **Data Storage & Data Warehouse**: PostgreSQL
- **Data Transformation & Modeling**: dbt (Data Build Tool)
- **Machine Learning & NLP**: Scikit-Learn, joblib, langdetect
- **Containerization**: Docker & Docker Compose

---


## ⚙️ Prerequisites

Before running this project locally, ensure you have the following tools installed:

- **[Docker](https://www.docker.com/)** and **Docker Compose** (Required to run Airflow, PostgreSQL, and Redis).
- **[Python 3.12+](https://www.python.org/)** (Required to run the FastAPI scraper service and local scripts).

---

## 📁 Directory Tree

Here is a detailed breakdown of the project structure:

```text
Data_Warehouse/
├── dags/
│   └── dag_ingestion_reviews.py     # Main orchestration pipeline
├── dbt_bank_reviews/                # dbt Project for Data Transformation
│   ├── models/               
│   │   ├── staging/                 # Initial data cleaning and formatting
│   │   └── marts/                   # Fact and Dimension tables (Star schema)
│   ├── dbt_project.yml              # Core dbt configuration
│   └── profiles.yml                 # Connection configuration to Postgres
├── scripts/                         # Web Scraping & APIs
│   ├── scraper_api.py               # FastAPI app exposing the /scrape endpoint
│   ├── script_reviews.py            # Selenium logic for extracting user reviews
│   └── script_bank.py               # Selenium logic for bank locations
├── ml_models/                       # NLP Serialized Models
│   ├── lda_model_v1.joblib          # Topic modeling (Latent Dirichlet Allocation)
│   └── vectorizer_v1.joblib         # TF-IDF Vectorizer
├── data/                            # Raw data files
│   └── reviews.csv                  # Output from the scraper
├── docker-compose.yaml              # Docker infrastructure (Airflow, Postgres, Redis)
├── train.ipynb                      # ML models training and evaluation notebook
├── .env.example                     # Environment variables template
└── requirements.txt                 # Python dependencies
```

---

## 🚀 Installation & Setup

Follow these exact steps to initialize and start the project from scratch.

**1. Initialization & Environment Setup**
You must configure your environment variables before launching the services.
- Create a `.env` file at the root of the project based on the provided `.env.example` file.
  ```env
  AIRFLOW_UID=50000
  FERNET_KEY=your_generated_secret_fernet_key
  DBNAME= your_database_name
  USER= your_database_username
  PASSWORD=your_database_password
  HOST=your_database_host
  PORT=your_database_port
  ```
- Configure your connection to the PostgreSQL database for dbt by creating or modifying the `profiles.yml` file inside the `dbt_bank_reviews/` directory.

**2. Prepare the Python Environment**
```bash
# Create and activate a virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Linux/Mac:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**3. Start the FastAPI Scraper Service**
Since Airflow uses an `HttpOperator` to trigger the scraping, you must run the FastAPI server locally (or inside its own container). Open a terminal, activate your virtual environment, and run:
```bash
cd scripts
uvicorn scraper_api:app --host 0.0.0.0 --port 8000 --reload
```

**4. Start the Infrastructure with Docker**
Open a new terminal, make sure Docker Desktop is running, then execute the following command at the root of the project:
```bash
# Start containers in the background (Airflow, PostgreSQL, Redis)
docker-compose up -d
```

**5. Access the Airflow UI & Configure Connection**
- Open your browser and go to `http://localhost:8080`.
- Log in with the default credentials (e.g., `airflow` / `airflow`).
- Go to **Admin > Connections** and ensure you have an HTTP connection named `scraper_api` pointing to your running FastAPI server (e.g., `http://host.docker.internal:8000`).
- Trigger the `dag_ingestion_reviews` DAG to start the pipeline.

---

## ✍️ Author
**Mustapha Dafa**

