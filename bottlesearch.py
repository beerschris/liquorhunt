import requests
from bs4 import BeautifulSoup

# The "Sensor" Target
TARGET_BRAND = "CAZCANES"
# Portland Metro Store ID Whitelist (30mi Radius)
PORTLAND_STORES = ['1168', '1152', '1024', '1165', '1061', '1106', '1150', '1251', '1051']

def scan_liquor_inventory():
    url = f"http://www.oregonliquorsearch.com/servlet/FrontController?view=browserecord&action=select&productSearchDesc={TARGET_BRAND}"
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Logic to find the inventory table
    # OLCC uses a standard <table> for results
    results = []
    table = soup.find('table', {'class': 'listing'})
    
    if table:
        for row in table.find_all('tr')[1:]: # Skip header
            cols = row.find_all('td')
            store_id = cols[0].text.strip()
            
            if store_id in PORTLAND_STORES:
                item = {
                    "brand": TARGET_BRAND,
                    "product": cols[1].text.strip(),
                    "store": cols[2].text.strip(),
                    "stock": int(cols[3].text.strip())
                }
                results.append(item)
    
    return results

# Then logic to UPSERT to Supabase goes here...
