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
            file_url = url + match if match.startswith("/") else match if match.startswith("http") else f"{url}/{match}" # If the URL is not absolute, append the base URL
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

@app.command()
def download(output_dir: str = "./downloads"):
    urls_7z = [
        "https://archive.org/download/nointro.gb",
        "https://archive.org/download/nointro.gbc",
        "https://archive.org/download/nointro.gba",
        "https://archive.org/download/nointro.snes",
        "https://archive.org/download/nointro.md",
        "https://archive.org/download/nointro.nes-headered"
    ]

    core_folder_mapping_7z = {
        urls_7z[0]: "Nintendo - GameBoy",
        urls_7z[1]: "Nintendo - GameBoy Color",
        urls_7z[2]: "Nintendo - GameBoy Advance",
        urls_7z[3]: "Nintendo - Super Nintendo Entertainment System",
        urls_7z[4]: "Sega - Mega Drive - Genesis",
        urls_7z[5]: "Nintendo - Nintendo Entertainment System"
    }

    urls_zip = [
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy/",
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20%28Private%29/",
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20Advance/",
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20Color/"
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Super%20Nintendo%20Entertainment%20System/",
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%20Entertainment%20System%20%28Headered%29/"
    ]

    core_folder_mapping_zip = {
        urls_zip[0]: "Nintendo - GameBoy",
        urls_zip[1]: "Nintendo - GameBoy (Private)",
        urls_zip[2]: "Nintendo - GameBoy Advance",
        urls_zip[3]: "Nintendo - GameBoy Color",
        urls_zip[4]: "Nintendo - Super Nintendo Entertainment System",
        urls_zip[5]: "Nintendo - Nintendo Entertainment System"
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with ThreadPoolExecutor(max_workers=max(len(urls_7z), len(urls_zip))) as executor:
        with Progress() as progress:
            task_id_7z = progress.add_task("Download .7z files", total=len(urls_7z))
            task_id_zip = progress.add_task("Download .zip files", total=len(urls_zip))

            # Schedule .7z downloads
            futures_7z = {url: executor.submit(download_7z_files, url, output_path, core_folder_mapping_7z, progress, task_id_7z) for url in urls_7z}

            # Schedule .zip downloads
            futures_zip = {url: executor.submit(download_zip_files, url, output_path) for url in urls_zip}

            # Wait for all futures to complete
            for future in as_completed(list(futures_7z.values()) + list(futures_zip.values())):  # Combine the list of futures
                try:
                    future.result()
                except Exception as e:
                    console.log(Text(f"Error processing future: {str(e)}", style="red"))
    console.print(Text("All files have been downloaded to the specified directory.", style="bold"))

if __name__ == "__main__":
    start_time = time.time()
    app()
    end_time = time.time()
    elapsed_time = end_time - start_time
    console.print(Text(f"Elapsed time: {elapsed_time:.2f} seconds", style="bold"))
