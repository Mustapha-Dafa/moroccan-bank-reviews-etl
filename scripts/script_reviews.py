from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import glob
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CITIES_DIR = PROJECT_ROOT / "data" / "cities"
REVIEWS_DIR = PROJECT_ROOT / "data" 


def format_relative_date(date_str):
    if not isinstance(date_str, str):
        return date_str
        
    # Chain cleaning
    s = date_str.lower().replace('modifié', '').strip()
    if 'une ' in s: # Replace "un/une" with the number 1.
            s = s.replace('une', '1')
    else :
            s = s.replace('un', '1')
    
    # Determination of the number and the unit (jour, semaine, mois, an)
    match = re.search(r'il y a (\d+)\s*(jour|semaine|mois|an)', s)
    
    if match:
        qty = int(match.group(1))
        unit = match.group(2)
        now = pd.Timestamp.now()
        
        # Subtraction of time according to the unit
        if 'jour' in unit:
            past_date = now - pd.DateOffset(days=qty)
        elif 'semaine' in unit:
            past_date = now - pd.DateOffset(weeks=qty)
        elif 'mois' in unit:
            past_date = now - pd.DateOffset(months=qty)
        elif 'an' in unit:
            past_date = now - pd.DateOffset(years=qty)
            
        return past_date.strftime('%d/%m/%y') # Format jj/mm/yy
        
    return date_str


def make_driver(headless=False):
    from selenium.webdriver.chrome.options import Options
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(2)  
    return driver

def scroll_reviews(driver, scrolls=25, pause=1.3):
    """Scroll inside the reviews panel to load more reviews."""
    panel = driver.find_element(By.XPATH, "//div[contains(@class,'m6QErb DxyBCb kA9KIf dS8AEf XiKgde')]")
    last_height = 0
    for _ in range(scrolls):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", panel)
        time.sleep(pause)
        new_height = driver.execute_script("return arguments[0].scrollHeight", panel)
        if new_height == last_height:
            break
        last_height = new_height

def extract_rating(card):
    """Retourne la note trouvée, sinon '' """
    try:
        elem = card.find_element(By.XPATH, ".//span[contains(@class,'kvMYJc') or contains(@class,'fontBodyLarge fzvQIb')]")
        rating = elem.get_attribute("aria-label") or elem.text
        return rating.strip()
    except:
        return ""
    
def get_reviews(driver, place_url, max_reviews=50):
    reviews = []
    
    driver.get(place_url)
    wait = WebDriverWait(driver, 10)

    try:
        # Click on the "Reviews" button
        reviews_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label,'Avis') or contains(@aria-label,'Reviews')]")))
        reviews_btn.click()

        # Scroll to load reviews
        scroll_reviews(driver)

        # Collect review cards
        cards = driver.find_elements(By.XPATH, "//div[contains(@class,'jftiEf')]")
        if len(cards)>50:
            max_reviews=50
        else:
            max_reviews=len(cards)
        for card in cards[:max_reviews]:

            rating = extract_rating(card)
            try:
                date = card.find_element(By.XPATH, ".//span[contains(@class,'xRkPPb') or contains(@class, 'rsqaWe')]").text
            except:
                date = ""

            try:
                text = card.find_element(By.XPATH, ".//span[contains(@class,'wiI7pd')]").text
            except:
                text = ""

            reviews.append({ "note": rating, "date": date,"date modifié": str(date).split("sur")[0] ,"review text": text})
            
    except Exception as e:
        print(f"[WARN] Could not scrape {place_url} – {e}")
    finally:
        driver.quit()
    return reviews

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)



def run_scraper():
    all_files = glob.glob(str(CITIES_DIR / "*.csv"))
    df_list = [pd.read_csv(file) for file in all_files]

    df = pd.concat(df_list, ignore_index=True)

    reviews=[]
    for i in range(len(df)):
        url=df.iloc[i]["link"]
        print(f"scraping {df.iloc[i]['category']} of {df.iloc[i]['place name']} from {df.iloc[i]['city']}")
        driver=make_driver()
        results=get_reviews(driver, url)
        results=pd.DataFrame(results)
        
        for j in range(len(results)):
            reviews.append({
                "city":df.iloc[i]["city"],
                "bank_name":df.iloc[i]["place name"],
                "review_date" : format_relative_date(results.iloc[j]["date modifié"]),
                "location":df.iloc[i]["address"] + ' ' + df.iloc[i]["city"] if df.iloc[i]["city"] not in df.iloc[i]["address"] else df.iloc[i]["address"],
                "rating": results.iloc[j]["note"].split('\xa0')[0] ,
                "review_text":results.iloc[j]["review text"]
            })
            
    output_file = REVIEWS_DIR / "reviews_test.csv"
    save_to_csv(reviews, output_file)

    return {
            "status": "success",
            "reviews_count": len(reviews),
            "output_file": output_file
        }

