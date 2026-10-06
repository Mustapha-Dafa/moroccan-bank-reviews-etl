from fastapi import FastAPI, HTTPException
from script_reviews import run_scraper

app = FastAPI(
    title="Bank Reviews Scraper API",
    description="API for scraping Google Maps bank reviews",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Bank Reviews Scraper API"
    }


@app.post("/scrape")
def scrape():
    try:
        result = run_scraper()

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )