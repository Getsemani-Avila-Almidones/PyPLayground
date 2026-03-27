import os
import re
import shutil
from pathlib import Path

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


def get_images_in_folder(folder: Path) -> list[Path]:
    return [p for p in folder.rglob("*") if is_image_file(p)]


def unique_destination(dest_dir: Path, base_name: str, suffix: str) -> Path:
    target = dest_dir / f"{base_name}{suffix}"
    if not target.exists():
        return target

    counter = 1
    while True:
        candidate = dest_dir / f"{base_name}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def process_item_folder(item_folder: Path) -> bool:
    images = get_images_in_folder(item_folder)

    # Solo procesar si hay exactamente 1 imagen
    if len(images) != 1:
        print(f"Saltando {item_folder} -> tiene {len(images)} imágenes")
        return False

    image = images[0]
    expected_name = f"{item_folder.name}{image.suffix.lower()}"
    destination = item_folder / expected_name

    # Si ya está bien nombrado, no hacer nada
    if image.resolve() == destination.resolve():
        print(f"Ya está OK: {image}")
        return False

    # Si existe un archivo con el nombre correcto, no pisar nada
    if destination.exists():
        print(f"Saltando {item_folder} -> ya existe {destination}")
        return False

    if DRY_RUN:
        print(f"[DRY-RUN] Renombrar: {image} -> {destination}")
    else:
        shutil.move(str(image), str(destination))
        print(f"Renombrado: {image} -> {destination}")

    return True


def process(root_path: Path):
    total_items = 0
    renamed = 0
    skipped = 0

    candidates = []

    for dirpath, _, _ in os.walk(root_path):
        current_dir = Path(dirpath)
        if is_item_folder(current_dir):
            candidates.append(current_dir)

    candidates.sort(key=lambda p: len(p.parts), reverse=True)

    for item_folder in candidates:
        total_items += 1
        if process_item_folder(item_folder):
            renamed += 1
        else:
            skipped += 1

    print("\n====================")
    print(f"Items encontrados: {total_items}")
    print(f"Renombrados: {renamed}")
    print(f"Omitidos: {skipped}")
    print("====================")


if __name__ == "__main__":
    if not ROOT_PATH.exists():
        raise FileNotFoundError(f"No existe la ruta: {ROOT_PATH}")

    process(ROOT_PATH)