## WARNING: This script is for **educational purposes only**. 
# Please ensure you have permission before scraping any website.
# Change the URL before using it for practical purposes

import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

MAX_IMAGES = 10  #how many images you need
START_PAGE = 1 # total pages you want to laod 
DOWNLOAD_FOLDER = "E:/allinone"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

scrape_session = requests.Session()
scrape_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://wallhaven.cc/",
    "Accept-Language": "en-US,en;q=0.9",
})

SEARCH_URL = "https://wallhaven.cc/search?categories=100&purity=100&atleast=2560x1440&sorting=random&order=asc&ai_art_filter=0&page={}"

def get_wallpaper_links(page):
    try:
        print(f"Searching page {page}...")
        res = scrape_session.get(SEARCH_URL.format(page), timeout=15)
        soup = BeautifulSoup(res.content, "html.parser")
        return [a["href"] for fig in soup.find_all("figure") if (a := fig.find("a", href=True)) and "/w/" in a["href"]]
    except Exception as e:
        print(f"Failed to get links from page {page}: {e}")
        return []

def get_image_url(detail_url):
    try:
        time.sleep(random.uniform(0.2, 0.5))
        res = scrape_session.get(detail_url, timeout=15)
        soup = BeautifulSoup(res.content, "html.parser")
        img = soup.find("img", id="wallpaper")
        return img["src"] if img else None
    except Exception as e:
        print(f"Error in detail page {detail_url}: {e}")
        return None

def download_image(url, index):
    try:
        filename = os.path.basename(urlparse(url).path)
        safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", filename).strip()
        filepath = Path(DOWNLOAD_FOLDER) / safe_name

        res = scrape_session.get(url, timeout=20)
        if res.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(res.content)
            print(f"{index:03d} Downloaded: {safe_name}")
        else:
            print(f"{index:03d} Failed (Status {res.status_code}) for {url}")
    except Exception as e:
        print(f"{index:03d} Download failed for {url}: {e}")

def collect_image_urls(max_images):
    collected_urls = set()
    page = START_PAGE

    with ThreadPoolExecutor(max_workers=4) as executor:
        while len(collected_urls) < max_images:
            future = executor.submit(get_wallpaper_links, page)
            detail_links = future.result()

            if not detail_links:
                print("Waiting before retry...")
                time.sleep(2)
                continue

            for link in detail_links:
                if len(collected_urls) >= max_images:
                    break
                if link in collected_urls:
                    continue

                image_url = get_image_url(link)
                if image_url:
                    collected_urls.add(image_url)
                    print(f"Found: {image_url}")

            page += 1
            time.sleep(random.uniform(0.2, 0.4))

    return list(collected_urls)

def main():
    collected_urls = collect_image_urls(MAX_IMAGES)
    
    print(f"\nStarting download of {len(collected_urls)} images...\n")
    for i, url in enumerate(collected_urls, start=1):
        download_image(url, i)

if __name__ == "__main__":
    main()
