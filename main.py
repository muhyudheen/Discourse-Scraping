import requests
import os
from dotenv import load_dotenv

load_dotenv()

cookies = json.loads(os.getenv("SCRAPING_COOKIES"))

headers = json.loads(os.getenv("SCRAPING_HEADERS"))

os.makedirs('data', exist_ok=True)

for page in range(1, 11):
    params= {
        "period": "all",
        "order": "likes_recieved",
        "page": str(page),
    }
    
    response = requests.get('https://discourse.onlinedegree.iitm.ac.in/directory_items',
                            params=params, cookies=cookies, headers=headers)
    
    data = response.json()
    
    with open(f"data/page_{page}.json", 'w', encoding='utf-8') as f:
        import json
        json.dump(data,f, indent=2)
        
    print(f"saved page {page}")