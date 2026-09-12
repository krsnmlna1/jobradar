import sys

from pathlib import Path
from playwright.sync_api import sync_playwright

def probe(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        response = page.goto(url)
        print(response.status, page.title(), len(page.content()))
        
        Path("/tmp/kalibrr.html").write_text(page.content(), encoding="utf-8")
        browser.close()
    
if __name__ == "__main__":
    url = sys.argv[1]
    probe(url)