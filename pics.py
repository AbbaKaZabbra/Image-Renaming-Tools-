import os
from pathlib import Path
from datetime import datetime

from PIL import Image, ExifTags
from pillow_heif import register_heif_opener

# Enable HEIC support
register_heif_opener()

# Folder to scan
folder = r"YOUR FOLDER HERE"#put your filepath in the qoutes

# Supported file types
extensions = {
    ".jpg",
    ".jpeg",
    ".png",
    ".heic",
    ".webp",
    ".tiff",
    ".bmp",
    ".gif",
    ".mov",
    ".mp4"
}

# Find the EXIF tag for "Date Taken"
DATE_TAG = next(
    k for k, v in ExifTags.TAGS.items()
    if v == "DateTimeOriginal"
)


def get_best_timestamp(file_path):
    """Return EXIF Date Taken if available, otherwise file modified time."""

    try:
        with Image.open(file_path) as img:
            exif = img.getexif()

            if exif:
                date_taken = exif.get(DATE_TAG)

                if date_taken:
                    return datetime.strptime(
                        date_taken,
                        "%m:%d%Y: %H:%M:%S"
                    )

    except Exception:
        pass

    # Fallback
    return datetime.fromtimestamp(os.path.getmtime(file_path))


def rename_file(file_path):
    path = Path(file_path)

    timestamp = get_best_timestamp(file_path)
    base_name = timestamp.strftime("%Y-%m-%d_%H-%M-%S")

    counter = 0

    while True:
        if counter == 0:
            new_name = f"{base_name}{path.suffix.lower()}"
        else:
            new_name = f"{base_name}({counter}){path.suffix.lower()}"

        new_path = path.with_name(new_name)

        if not new_path.exists():
            break

        counter += 1

    # Skip if already correctly named
    if path == new_path:
        print(f"Skipping: {path.name}")
        return

    print(f"{path.name}  ->  {new_path.name}")
    os.rename(path, new_path)


def scan_folder(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            path = Path(root) / file

            if path.suffix.lower() in extensions:
                rename_file(path)


if __name__ == "__main__":
    scan_folder(folder)
    print("\nDone!")