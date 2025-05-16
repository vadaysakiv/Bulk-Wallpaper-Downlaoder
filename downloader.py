import os
import requests
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from tqdm import tqdm

# Folder for saving wallpapers
folder_name = "E:/wallhaven"
os.makedirs(folder_name, exist_ok=True)

# Base URLs
base_page_url = "https://wallhaven.cc/search?q=id%3A37&sorting=random&ref=fp&seed=QeEXQc&page={}"
base_image_url = "https://w.wallhaven.cc/full/{}/wallhaven-{}.jpg"  # Wallpaper link format

def get_wallpaper_links():
    """Scrapes wallpaper href links from multiple Wallhaven pages."""
    wallpaper_ids = set()  # Use a set to avoid duplicates

    for page in range(1, 40):  # Loop through pages 1 to 20
        page_url = base_page_url.format(page)
        response = requests.get(page_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            wallpapers = soup.find_all("a", class_="preview")  # Extract wallpaper preview links
            wallpaper_ids.update(wall.get("href").split("/")[-1] for wall in wallpapers)

    return list(wallpaper_ids)[:100]  # Limit to 100 images

async def download_wallpaper(session, wallpaper_id):
    """Downloads a single wallpaper asynchronously."""
    image_url = base_image_url.format(wallpaper_id[:2], wallpaper_id)
    image_name = f"wallhaven_{wallpaper_id}.jpg"

    try:
        async with session.get(image_url) as response:
            if response.status == 200:
                with open(os.path.join(folder_name, image_name), 'wb') as file:
                    file.write(await response.read())
                print(f"Downloaded: {image_name}")
            else:
                print(f"Skipping: {image_name} (Status Code: {response.status})")
    except Exception as e:
        print(f"Error downloading {image_name}: {e}")

async def async_download():
    """Uses asyncio for fast parallel downloads."""
    wallpaper_ids = get_wallpaper_links()

    async with aiohttp.ClientSession() as session:
        tasks = [download_wallpaper(session, wallpaper_id) for wallpaper_id in wallpaper_ids]
        for _ in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            await _

    print("\nDownload complete!")

if __name__ == "__main__":
    asyncio.run(async_download())
