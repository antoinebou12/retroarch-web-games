import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_7z_files(url):
    response = requests.get(url)
    pattern = re.compile(r'<td><a href="([^"]+\.7z)')
    matches = pattern.findall(response.text)
    
    if matches:
        file_url = f"{url}/{matches[0]}"
        filename = file_url.split("/")[-1]
        response = requests.get(file_url)
        
        with open(filename, "wb") as f:
            f.write(response.content)

        print(f"Downloaded {filename}")

urls = [
    "https://archive.org/download/nointro.gb",
    "https://archive.org/download/nointro.gbc",
    "https://archive.org/download/nointro.gba",
    "https://archive.org/download/nointro.snes",
    "https://archive.org/download/nointro.md",
    "https://archive.org/download/nointro.nes-headered"
]

with ThreadPoolExecutor(max_workers=6) as executor:
    futures = {executor.submit(download_7z_files, url): url for url in urls}
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"Error downloading: {str(e)}")
