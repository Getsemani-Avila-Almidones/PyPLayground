import os
from pathlib import Path
from utils.helpers import is_item_folder, folder_contains_images


def scan_item_folders(root_path: Path) -> tuple[list[Path], dict]:
    """
    Escanea el directorio raíz buscando carpetas de items con imágenes.

    Returns:
        tuple: (lista de carpetas de items, estadísticas)
    """
    item_folders = []
    stats = {
        "total_found": 0,
        "with_images": 0,
        "without_images": 0
    }

    for dirpath, _, _ in os.walk(root_path):
        current_dir = Path(dirpath)

        if is_item_folder(current_dir):
            stats["total_found"] += 1

            if folder_contains_images(current_dir):
                stats["with_images"] += 1
                item_folders.append(current_dir)
            else:
                stats["without_images"] += 1

    return item_folders, stats


def scan_semana_folders(root_path: Path) -> tuple[list[Path], dict]:
    """
    Escanea el directorio raíz buscando carpetas SEMANA.

    Returns:
        tuple: (lista de carpetas SEMANA, estadísticas)
    """
    semana_folders = []
    stats = {
        "total": 0,
        "with_files": 0,
        "empty": 0
    }

    for dirpath, _, _ in os.walk(root_path):
        current_dir = Path(dirpath)

        if current_dir.name.startswith("SEMANA"):
            stats["total"] += 1
            semana_folders.append(current_dir)

            # Verificar si tiene archivos
            has_files = any(current_dir.rglob("*"))
            if has_files:
                stats["with_files"] += 1
            else:
                stats["empty"] += 1

    return semana_folders, stats
