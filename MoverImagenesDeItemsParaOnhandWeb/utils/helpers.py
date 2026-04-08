import hashlib
from pathlib import Path
from config import IMAGE_EXTENSIONS, ITEM_PATTERN, HASH_CHUNK_SIZE


def is_image_file(path: Path) -> bool:
    """Verifica si un archivo es una imagen según su extensión."""
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def is_item_folder(path: Path) -> bool:
    """Verifica si una carpeta cumple con el patrón de nombre de item."""
    return path.is_dir() and ITEM_PATTERN.match(path.name) is not None


def get_images_in_folder(folder: Path) -> list[Path]:
    """Obtiene todas las imágenes dentro de una carpeta (recursivamente)."""
    return [p for p in folder.rglob("*") if is_image_file(p)]


def folder_contains_images(folder: Path) -> bool:
    """Verifica si una carpeta contiene al menos una imagen."""
    for img_path in folder.rglob("*"):
        if is_image_file(img_path):
            return True
    return False


def file_hash(path: Path) -> str:
    """Calcula el hash SHA256 de un archivo."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(HASH_CHUNK_SIZE)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def unique_destination_dir(root_path: Path, folder_name: str) -> Path:
    """
    Genera un nombre único para un directorio de destino.
    Si ya existe, agrega un sufijo numérico.
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
