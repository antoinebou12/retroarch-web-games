import re
import requests
import typer
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.text import Text
from concurrent.futures import as_completed
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote
import time

app = typer.Typer()
console = Console()


def simplify_filename(filename: str) -> str:
    filename = unquote(filename)
    file_ext = ".7z" if filename.endswith(".7z") else ".zip"
    filename = re.sub(r"\(.*?\)", "", filename, flags=re.DOTALL)
    filename = re.sub(r"[^a-zA-Z0-9]+", "_", filename)
    return f"{filename.strip('_')}{file_ext}"


def download_zip_files(
    url: str,
    output_dir: Path,
    core_folder_mapping: dict,
    progress: Progress,
    task_id: int,
):
    start_time = time.time()
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        console.print(
            Text(
                f"An error occurred while trying to connect to {url}. Please check your internet connection.",
                style="red",
            )
        )
        return
    except requests.exceptions.RequestException as e:
        console.print(
            Text(
                f"An error occurred while trying to connect to {url}: {str(e)}",
                style="red",
            )
        )
        return
    pattern = re.compile(r'<td><a href="([^"]+\.zip)')
    matches = pattern.findall(response.text)
    total_games = len(matches)

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

        end_time = time.time()
        elapsed_time = end_time - start_time
        console.print(
            Text(
                f"Thread for {core_folder_mapping[url]} completed in {elapsed_time:.2f} seconds for {total_games} games",
                style="green",
            )
        )
        progress.update(task_id, advance=1)


def download_file(
    file_url: str,
    output_dir: Path,
    simple_name: str,
    progress: Progress,
    task_id: TaskID,
):
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        original_file_path = output_dir / simple_name
        with original_file_path.open("wb") as f:
            f.write(response.content)
        console.print(Text(f"Downloaded and renamed {simple_name}", style="green"))
        progress.update(task_id, advance=1)
    except requests.RequestException as e:
        console.print(Text(f"Failed to download {file_url}: {e}", style="red"))



def download_files(
    url: str,
    output_dir: Path,
    core_folder_mapping: dict,
    progress: Progress,
    task_id: TaskID,
):
    start_time = time.time()
    try:
        response = requests.get(url)
        response.raise_for_status()
        matches = re.findall(r'<a href="([^"]+\.(?:zip|7z))"', response.text)
        if not matches:
            console.print(Text(f"No files found at {url}.", style="yellow"))
            return
        target_folder = core_folder_mapping[url]
        target_dir = output_dir / target_folder
        target_dir.mkdir(parents=True, exist_ok=True)

        with ThreadPoolExecutor() as executor:
            for match in matches:
                file_url = f"{url}/{match}"
                simple_name = simplify_filename(match.split("/")[-1])
                executor.submit(
                    download_file, file_url, target_dir, simple_name, progress, task_id
                )
    except requests.RequestException as e:
        console.print(Text(f"Failed to access {url}: {e}", style="red"))
    finally:
        end_time = time.time()
        console.print(
            Text(
                f"Completed downloads from {url} in {end_time - start_time:.2f} seconds.",
                style="bold green",
            )
        )


@app.command()
def download(output_dir: str = "./downloads"):
    urls_7z = [
        "https://archive.org/download/nointro.gb",
        "https://archive.org/download/nointro.gbc",
        "https://archive.org/download/nointro.gba",
        "https://archive.org/download/nointro.snes",
        "https://archive.org/download/nointro.md",
        "https://archive.org/download/nointro.nes-headered",
    ]

    core_folder_mapping_7z = {
        urls_7z[0]: "Nintendo - GameBoy",
        urls_7z[1]: "Nintendo - GameBoy Color",
        urls_7z[2]: "Nintendo - GameBoy Advance",
        urls_7z[3]: "Nintendo - Super Nintendo Entertainment System",
        urls_7z[4]: "Sega - Mega Drive - Genesis",
        urls_7z[5]: "Nintendo - Nintendo Entertainment System",
    }

    urls_zip = [
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy/",
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20%28Private%29/",
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20Advance/",
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20Color/",
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Super%20Nintendo%20Entertainment%20System/",
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%20Entertainment%20System%20%28Headered%29/",
        "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Nintendo%2064%20%28BigEndian%29/",
    ]

    core_folder_mapping_zip = {
        urls_zip[0]: "Nintendo - GameBoy",
        urls_zip[1]: "Nintendo - GameBoy",
        urls_zip[2]: "Nintendo - GameBoy Advance",
        urls_zip[3]: "Nintendo - GameBoy Color",
        urls_zip[4]: "Nintendo - Super Nintendo Entertainment System",
        urls_zip[5]: "Nintendo - Nintendo Entertainment System",
        urls_zip[6]: "Nintendo - Nintendo 64",
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with Progress() as progress:
        task_id_7z = progress.add_task("Downloading 7z files", total=len(urls_7z))
        task_id_zip = progress.add_task("Downloading zip files", total=len(urls_zip))

        with ThreadPoolExecutor() as executor:
            for url in urls_7z:
                executor.submit(
                    download_files,
                    url,
                    output_path,
                    core_folder_mapping_7z,
                    progress,
                    task_id_7z,
                )

            for url in urls_zip:
                executor.submit(
                    download_files,
                    url,
                    output_path,
                    core_folder_mapping_zip,
                    progress,
                    task_id_zip,
                )

if __name__ == "__main__":
    start_time = time.time()
    app()
    end_time = time.time()
    elapsed_time = end_time - start_time
    console.print(Text(f"Elapsed time: {elapsed_time:.2f} seconds", style="bold"))
