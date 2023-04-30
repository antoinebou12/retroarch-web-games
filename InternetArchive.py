import re
import requests
import typer
from rich.console import Console
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

app = typer.Typer()
console = Console()

def download_7z_files(url: str, output_dir: Path):
    response = requests.get(url)
    pattern = re.compile(r'<td><a href="([^"]+\.7z)')
    matches = pattern.findall(response.text)

    if matches:
        file_url = f"{url}/{matches[0]}"
        filename = file_url.split("/")[-1]
        response = requests.get(file_url)

        with open(output_dir / filename, "wb") as f:
            f.write(response.content)

        console.log(f"Downloaded {filename}")

@app.command()
def download(output_dir: str = "downloads"):
    urls = [
        "https://archive.org/download/nointro.gb",
        "https://archive.org/download/nointro.gbc",
        "https://archive.org/download/nointro.gba",
        "https://archive.org/download/nointro.snes",
        "https://archive.org/download/nointro.md",
        "https://archive.org/download/nointro.nes-headered"
    ]

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(download_7z_files, url, output_path): url for url in urls}
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                console.log(f"Error downloading: {str(e)}")

if __name__ == "__main__":
    app()
