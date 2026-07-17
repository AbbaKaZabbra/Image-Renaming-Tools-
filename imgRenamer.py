import os
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, scrolledtext

from PIL import Image, ExifTags
from pillow_heif import register_heif_opener

register_heif_opener()

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
    ".mp4",
}

DATE_TAG = next(
    k for k, v in ExifTags.TAGS.items()
    if v == "DateTimeOriginal"
)


# ---------------- Logging ----------------

def log(message):
    output.insert(tk.END, message + "\n")
    output.see(tk.END)
    root.update()


# ---------------- Image Functions ----------------

def get_best_timestamp(file_path):
    try:
        with Image.open(file_path) as img:
            exif = img.getexif()

            if exif:
                date_taken = exif.get(DATE_TAG)

                if date_taken:
                    return datetime.strptime(
                        date_taken,
                        "%Y:%m:%d %H:%M:%S"
                    )
                
    except Exception:
        pass

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

    if path == new_path:
        log(f"Skipping: {path.name}")
        return

    log(f"{path.name}  ->  {new_path.name}")
    os.rename(path, new_path)


def scan_folder(folder):
    output.delete("1.0", tk.END)

    count = 0

    for root_dir, dirs, files in os.walk(folder):
        for file in files:
            path = Path(root_dir) / file

            if path.suffix.lower() in extensions:
                rename_file(path)
                count += 1

    log("")
    log(f"Done! Processed {count} files.")


# ---------------- GUI ----------------

def browse_folder():
    folder = filedialog.askdirectory()

    if folder:
        folder_var.set(folder)


def start_scan():
    folder = folder_var.get()

    if not folder:
        log("Please choose a folder first.")
        return

    scan_folder(folder)


root = tk.Tk()
root.title("Photo Renamer")
root.geometry("800x600")

folder_var = tk.StringVar()

frame = tk.Frame(root)
frame.pack(fill="x", padx=10, pady=10)

entry = tk.Entry(frame, textvariable=folder_var)
entry.pack(side="left", fill="x", expand=True)

browse = tk.Button(frame, text="Browse", command=browse_folder)
browse.pack(side="left", padx=5)

scan = tk.Button(frame, text="Scan", command=start_scan)
scan.pack(side="left")

output = scrolledtext.ScrolledText(root, height=30)
output.pack(fill="both", expand=True, padx=10, pady=10)

root.mainloop()