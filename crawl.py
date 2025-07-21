# This is the crawler that was used to create the database for the search engine

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

START_URL = "https://en.wikipedia.org/wiki/Sword_Art_Online"
BASE_URL = "https://en.wikipedia.org"
MAX_PAGES = 5000
OUTPUT_FILE = "database.js"
visited = set()

if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("const database = [\n")

def clean_text(text):
    return text.replace("\n", " ").replace("'", "").replace('"', "").replace("`", "").strip()

def scrape_page(url):
    if url in visited:
        return
    visited.add(url)
    print(f"Crawling: {url}")
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        title_tag = soup.find('h1', {'id': 'firstHeading'})
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if not title_tag or not content_div:
            return
        title = clean_text(title_tag.text)
        paragraphs = content_div.find_all('p', recursive=True)
        if not paragraphs:
            return
        desc = clean_text(paragraphs[0].text)
        html_content = ""
        for tag in paragraphs[:5]:
            html_content += str(tag)
        html_content = clean_text(html_content)
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(f"  {{\n    title: '{title}',\n")
            f.write(f"    desc: '{desc}',\n")
            f.write(f"    htmlContent: `\n      {html_content}\n    `\n  }},\n")
        links = content_div.find_all('a', href=True)
        count = 0
        for link in links:
            href = link['href']
            full_url = urljoin(BASE_URL, href)
            if '/wiki/' in href and ':' not in href and full_url not in visited:
                scrape_page(full_url)
                count += 1
                if count > 5:
                    break
    except:
        pass

scrape_page(START_URL)
