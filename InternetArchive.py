import re
import requests
import typer
from rich.console import Console
from rich.progress import Progress
from rich.text import Text
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import unquote

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

def download_7z_files(url: str, output_dir: Path, core_folder_mapping: dict, progress: Progress, task_id: int):
    response = requests.get(url)
    pattern = re.compile(r'<td><a href="([^"]+\.7z)')
    matches = pattern.findall(response.text)

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

        console.print(Text(f"Renamed {filename} to {simple_name}", style="blue"))

    # Update progress
    progress.update(task_id, advance=1)

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
        with Progress() as progress:
            task_id = progress.add_task("Download and rename files", total=len(urls))

            futures = {executor.submit(download_7z_files, url, output_path, core_folder_mapping, progress, task_id): url for url in urls}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    console.log(Text(f"Error downloading: {str(e)}", style="red"))
    console.print(Text(f"All .7z files have been downloaded to {output_dir}.", style="bold"))

if __name__ == "__main__":
    app()
