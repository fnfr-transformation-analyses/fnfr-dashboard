from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re


def scrape_researchgate_publications(query: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=50)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36")
    
        page.goto(f"https://www.researchgate.net/search/researcher?q={query}")
        text = page.locator("body").text_content() 
        browser.close()

        with open("dev__content.txt", 'w', encoding='utf-8') as f:
            f.write(text)

        with open("dev__skills.txt", 'w', encoding='utf-8') as f:
            pattern = '"skills":\[(\{"name":".+","isPromoted":(true|false)\})+\]'
            skills = re.findall(pattern, text)[0][0]
            skills = skills.split('"],"publication')[0]
            f.write(skills)
        
    
scrape_researchgate_publications(query="Jennifer Bethell")