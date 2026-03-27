import os
import re
import shutil
from pathlib import Path

# =========================
# CONFIGURACIÓN
# =========================
ROOT_PATH = Path(r"C:\Users\21596\Documents\Dev\rptOnHandWeb\assets\items")  # cambia esto
DRY_RUN = False

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tif", ".tiff", ".jfif", ".avif", ".svg"}

# Ejemplo:
# 120-005-003
# N-120-005-003
# A-120-005-003
ITEM_PATTERN = re.compile(r"^(?:[A-Za-z]-)?[A-Za-z0-9]+-[A-Za-z0-9]+-[A-Za-z0-9]+$")


def is_image_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def is_item_folder(path: Path) -> bool:
    return path.is_dir() and ITEM_PATTERN.match(path.name) is not None


def folder_contains_images(folder: Path) -> bool:
    for root, _, files in os.walk(folder):
        for file_name in files:
            if is_image_file(Path(root) / file_name):
                return True
    return False


def unique_destination_dir(root_path: Path, folder_name: str) -> Path:
    """
    Evita sobrescribir una carpeta existente con el mismo nombre.
    """
    target = root_path / folder_name
    if not target.exists():
        return target

    counter = 1
    while True:
        candidate = root_path / f"{folder_name}_{counter}"
        if not candidate.exists():
            return candidate
        counter += 1


def move_item_folder_to_root(item_folder: Path, root_path: Path):
    destination = unique_destination_dir(root_path, item_folder.name)

    if DRY_RUN:
        print(f"[DRY-RUN] Mover carpeta: {item_folder} -> {destination}")
    else:
        shutil.move(str(item_folder), str(destination))
        print(f"Movida carpeta: {item_folder} -> {destination}")


def process_items(root_path: Path):
    found = 0
    moved = 0

    # Capturamos primero los candidatos antes de mover, para no romper el recorrido
    candidates = []

    for dirpath, dirnames, _ in os.walk(root_path):
        current_dir = Path(dirpath)

        if is_item_folder(current_dir):
            found += 1
            if folder_contains_images(current_dir):
                candidates.append(current_dir)

    for item_folder in candidates:
        move_item_folder_to_root(item_folder, root_path)
        moved += 1

    print("\n====================")
    print(f"Carpetas item encontradas: {found}")
    print(f"Carpetas item movidas: {moved}")
    print("====================")


if __name__ == "__main__":
    if not ROOT_PATH.exists():
        raise FileNotFoundError(f"No existe la ruta: {ROOT_PATH}")

    process_items(ROOT_PATH)