import os
import re
import hashlib
from pathlib import Path

ROOT_PATH = Path(r"C:\Users\21596\Documents\Dev\rptOnHandWeb\assets\items")  # cambia esto
DRY_RUN = False

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tif", ".tiff", ".jfif", ".avif", ".svg"}
ITEM_PATTERN = re.compile(r"^(?:[A-Za-z]-)?[A-Za-z0-9]+-[A-Za-z0-9]+-[A-Za-z0-9]+$")


def is_image_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def is_item_folder(path: Path) -> bool:
    return path.is_dir() and ITEM_PATTERN.match(path.name) is not None


def get_images_in_folder(folder: Path) -> list[Path]:
    return [p for p in folder.rglob("*") if is_image_file(p)]


def file_hash(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def process_item_folder(item_folder: Path) -> bool:
    images = get_images_in_folder(item_folder)

    if not images:
        print(f"Saltando {item_folder} -> sin imágenes")
        return False

    # Si ya existe un archivo con nombre correcto, úsalo como principal
    main_image = None
    for img in images:
        expected = item_folder / f"{item_folder.name}{img.suffix.lower()}"
        if expected.exists():
            main_image = expected
            break

    # Si no existe, renombrar la primera imagen encontrada al nombre del item
    if main_image is None:
        source = images[0]
        destination = item_folder / f"{item_folder.name}{source.suffix.lower()}"

        if source.resolve() != destination.resolve():
            if DRY_RUN:
                print(f"[DRY-RUN] Renombrar: {source} -> {destination}")
            else:
                if destination.exists():
                    destination.unlink()
                source.rename(destination)
                print(f"Renombrada: {source} -> {destination}")

        main_image = destination

    # IMPORTANTÍSIMO:
    # refrescar la lista después del renombrado para no usar rutas viejas
    images = get_images_in_folder(item_folder)

    # Borrar duplicados exactos, dejando solo el archivo principal
    main_hash = file_hash(main_image)

    for img in images:
        if img.resolve() == main_image.resolve():
            continue

        try:
            if file_hash(img) == main_hash:
                if DRY_RUN:
                    print(f"[DRY-RUN] Borrar duplicado: {img}")
                else:
                    img.unlink()
                    print(f"Borrado duplicado: {img}")
            else:
                print(f"AVISO: imagen distinta encontrada, no se tocó: {img}")
        except FileNotFoundError:
            # Por si el archivo ya fue movido/eliminado en el proceso
            continue

    return True


def process(root_path: Path):
    total_items = 0
    processed = 0
    skipped = 0

    candidates = []

    for dirpath, _, _ in os.walk(root_path):
        current_dir = Path(dirpath)
        if is_item_folder(current_dir):
            candidates.append(current_dir)

    candidates.sort(key=lambda p: len(p.parts), reverse=True)

    for item_folder in candidates:
        total_items += 1
        print(f"\nProcesando: {item_folder}")
        if process_item_folder(item_folder):
            processed += 1
        else:
            skipped += 1

    print("\n====================")
    print(f"Items encontrados: {total_items}")
    print(f"Items procesados: {processed}")
    print(f"Items omitidos: {skipped}")
    print("====================")


if __name__ == "__main__":
    if not ROOT_PATH.exists():
        raise FileNotFoundError(f"No existe la ruta: {ROOT_PATH}")

    process(ROOT_PATH)