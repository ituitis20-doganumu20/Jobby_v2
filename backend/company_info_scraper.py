from googlesearch import search
import requests
from bs4 import BeautifulSoup

def get_company_info(company_name):
    queries = [
        f"{company_name} site:linkedin.com",
        f"{company_name} about us site:{company_name.lower().replace(' ', '')}.com",
        f"{company_name} company overview",
    ]
    
    urls = set()
    for query in queries:
        for result in search(query, num_results=3):
            urls.add(result)

    info_text = ""
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = ' '.join([p.get_text() for p in soup.find_all('p')])
            if len(text) > 300:  # Basic quality filter
                info_text += f"\n\nSource: {url}\n{text[:1500]}..."  # Limit size
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
    
    return info_text.strip()
