import re
import requests
import typer
from rich.console import Console
from rich.progress import Progress
from rich.text import Text
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import unquote
import time

app = typer.Typer()
console = Console()

def simplify_filename(filename: str) -> str:
    # Decode URL-encoded characters
    filename = unquote(filename)

    # Extract the file extension
    file_ext = ".7z" if filename.endswith(".7z") else ""

    # Remove the file extension before simplifying the filename
    filename = filename.replace(file_ext, '')

    # Remove region and version information
    filename = re.sub(r'\(.*?\)', '', filename)

    # Replace special characters and spaces with underscores
    filename = re.sub(r'[^a-zA-Z0-9]+', '_', filename)

    # Re-add the file extension to the simplified filename
    return f"{filename.strip('_')}{file_ext}"

def download_zip_files(url: str, output_dir: Path):
    response = requests.get(url)
    if response.status_code == 200:
        # Adjust the pattern if the HTML structure is different
        pattern = re.compile(r'href="([^"]+\.zip)"')
        matches = pattern.findall(response.text)

        for match in matches:
            # Ensure the URL is absolute
            file_url = urljoin(url, match)
            filename = file_url.split("/")[-1]
            simple_name = simplify_filename(filename)

            # Download the file
            response = requests.get(file_url)
            if response.status_code == 200:
                (output_dir).mkdir(parents=True, exist_ok=True)
                file_path = output_dir / simple_name
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"Downloaded and saved: {simple_name}")
            else:
                print(f"Failed to download: {file_url}")
    else:
        print("Failed to fetch the webpage")


def download_7z_files(url: str, output_dir: Path, core_folder_mapping: dict, progress: Progress, task_id: int):
    start_time = time.time()
    response = requests.get(url)
    pattern = re.compile(r'<td><a href="([^"]+\.7z)')
    matches = pattern.findall(response.text)
    total_games = len(matches)
    games_downloaded = 0

    for match in matches:
        file_url = f"{url}/{match}"
        filename = file_url.split("/")[-1]
        response = requests.get(file_url)

        target_folder = core_folder_mapping[url]
        (output_dir / target_folder).mkdir(parents=True, exist_ok=True)

        # Download the file
        original_file_path = output_dir / target_folder / filename
        with open(original_file_path, "wb") as f:
            f.write(response.content)

        # Rename the file to a simpler name
        simple_name = simplify_filename(filename)
        renamed_file_path = output_dir / target_folder / simple_name
        original_file_path.rename(renamed_file_path)

        console.print(Text(f"{simple_name}", style="blue"))

        # Update progress
        games_downloaded += 1
        end_time = time.time()
        elapsed_time = end_time - start_time
        console.print(Text(f"Thread for {core_folder_mapping[url]} completed in {elapsed_time:.2f} seconds", style="green"))
        progress.update(task_id, advance=1)

def download_files(url: str, output_dir: Path, core_folder_mapping: dict, progress: Progress, task_id: int, file_ext: str):
    start_time = time.time()
    response = requests.get(url)
    pattern = re.compile(rf'href="([^"]+\{file_ext})"')
    matches = pattern.findall(response.text)
    for match in matches:
        file_url = urljoin(url, match)
        filename = file_url.split("/")[-1]
        response = requests.get(file_url)
        if response.status_code == 200:
            target_folder = core_folder_mapping[url]
            (output_dir / target_folder).mkdir(parents=True, exist_ok=True)
            file_path = output_dir / target_folder / simplify_filename(filename)
            with open(file_path, "wb") as f:
                f.write(response.content)
            console.print(Text(f"{simplify_filename(filename)}", style="blue"))
        else:
            console.print(Text(f"Failed to download: {filename}", style="red"))
    end_time = time.time()
    elapsed_time = end_time - start_time
    console.print(Text(f"Thread for {core_folder_mapping[url]} completed in {elapsed_time:.2f} seconds", style="green"))
    progress.update(task_id, advance=1)

@app.command()
def download(output_dir: str = "/var/www/html/assets/cores"):
    urls = [
        "https://archive.org/download/nointro.gb",
        "https://archive.org/download/nointro.gbc",
        "https://archive.org/download/nointro.gba",
        "https://archive.org/download/nointro.snes",
        "https://archive.org/download/nointro.md",
        "https://archive.org/download/nointro.nes-headered",
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy/",
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20%28Private%29/",
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20Advance/",
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20Color/"
    ]

    core_folder_mapping = {
        urls[0]: "Nintendo - GameBoy",
        urls[1]: "Nintendo - GameBoy Color",
        urls[2]: "Nintendo - GameBoy Advance",
        urls[3]: "Nintendo - Super Nintendo Entertainment System",
        urls[4]: "Sega - Mega Drive - Genesis",
        urls[5]: "Nintendo - Nintendo Entertainment System"
        urls[6]: "Nintendo - GameBoy",
        urls[7]: "Nintendo - GameBoy",
        urls[8]: "Nintendo - GameBoy Advance",
        urls[9]: "Nintendo - GameBoy Color",
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
        with Progress() as progress:
            task_id = progress.add_task("Download and rename files", total=len(urls))
            futures = []
            for url in urls:
                file_ext = ".zip" if "No-Intro/Nintendo" in url else ".7z"
                futures.append(executor.submit(download_files, url, output_path, core_folder_mapping, progress, task_id, file_ext))
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    console.log(Text(f"Error downloading: {str(e)}", style="red"))
    console.print(Text(f"All files have been downloaded to {output_dir}.", style="bold"))

if __name__ == "__main__":
    start_time = time.time()
    app()
    end_time = time.time()
    elapsed_time = end_time - start_time
    console.print(Text(f"Elapsed time: {elapsed_time:.2f} seconds", style="bold"))
