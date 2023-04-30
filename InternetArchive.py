import re
import requests
import typer
from rich.console import Console
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

app = typer.Typer()
console = Console()

def download_7z_files(url: str, output_dir: Path, core_folder_mapping: dict):
    response = requests.get(url)
    pattern = re.compile(r'<td><a href="([^"]+\.7z)')
    matches = pattern.findall(response.text)

    if matches:
        file_url = f"{url}/{matches[0]}"
        filename = file_url.split("/")[-1]
        response = requests.get(file_url)

        target_folder = core_folder_mapping[url]
        (output_dir / target_folder).mkdir(parents=True, exist_ok=True)

        with open(output_dir / target_folder / filename, "wb") as f:
            f.write(response.content)

        console.log(f"Downloaded {filename} to {target_folder}")

@app.command()
def download(output_dir: str = "/var/www/html/assets/cores"):
    urls = [
        "https://archive.org/download/nointro.gb",
        "https://archive.org/download/nointro.gbc",
        "https://archive.org/download/nointro.gba",
        "https://archive.org/download/nointro.snes",
        "https://archive.org/download/nointro.md",
        "https://archive.org/download/nointro.nes-headered"
    ]

    core_folder_mapping = {
        urls[0]: "Nintendo - GameBoy",
        urls[1]: "Nintendo - GameBoy Color",
        urls[2]: "Nintendo - GameBoy Advance",
        urls[3]: "Nintendo - Super Nintendo Entertainment System",
        urls[4]: "Sega - Mega Drive - Genesis",
        urls[5]: "Nintendo - Nintendo Entertainment System"
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(download_7z_files, url, output_path, core_folder_mapping): url for url in urls}
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                console.log(f"Error downloading: {str(e)}")

if __name__ == "__main__":
    app()
