import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

# 1. Setup Supabase Connection
url = os.environ.get("https://atxlgwfsgneoymcazyzy.supabase.co")
key = os.environ.get("sb_publishable_Lf_Grwcf8_uGf5Uiwm6Y4A_ZIPChWbN") # Use the SERVICE_ROLE_KEY here!
supabase = create_client(url, key)

# 2. Portland Metro Whitelist (30mi Radius)
PORTLAND_STORES = ['1168', '1152', '1024', '1165', '1061', '1106', '1150', '1251', '1051']
TARGET_BRAND = "CAZCANES"

def scrape_olcc():
    # OLCC Search URL
    search_url = f"http://www.oregonliquorsearch.com/servlet/FrontController?view=browserecord&action=select&productSearchDesc={TARGET_BRAND}"
    
    r = requests.get(search_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    found_items = []
    # OLCC results are usually in a table with class 'listing'
    table = soup.find('table', {'class': 'listing'})
    
    if table:
        for row in table.find_all('tr')[1:]: # Skip header
            cols = row.find_all('td')
            if len(cols) > 3:
                store_id = cols[0].text.strip()
                
                # The 30-Mile Filter
                if store_id in PORTLAND_STORES:
                    data = {
                        "category": "Tequila",
                        "brand": TARGET_BRAND,
                        "product_name": cols[1].text.strip(),
                        "store_id": store_id,
                        "store_name": cols[2].text.strip(),
                        "quantity": int(cols[3].text.strip()),
                        "last_updated": "now()" 
                    }
                    found_items.append(data)
    return found_items

def sync_to_supabase():
    items = scrape_olcc()
    for item in items:
        # Upsert: Match on product_name and store_id (our unique constraint)
        supabase.table("liquor_inventory").upsert(item, on_conflict="product_name,store_id").execute()
    print(f"Sweep complete. {len(items)} targets identified in Sector Portland.")

if __name__ == "__main__":
    sync_to_supabase()
