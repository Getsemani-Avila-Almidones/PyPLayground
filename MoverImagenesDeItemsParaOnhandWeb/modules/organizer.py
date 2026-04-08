import shutil
from pathlib import Path
from config import DRY_RUN
from utils.helpers import unique_destination_dir


def organize_item_folder(item_folder: Path, root_path: Path, verbose: bool = True) -> bool:
    """
    Mueve una carpeta de item al directorio raíz, creando la estructura:
    Items/<NumeroDeItem>/

    Args:
        item_folder: Carpeta de item a mover
        root_path: Directorio raíz de destino

    Returns:
        bool: True si se movió exitosamente
    """
    # La carpeta de destino será: root_path / nombre_del_item
    destination = unique_destination_dir(root_path, item_folder.name)

    # Si la carpeta ya está en el root, no hacer nada
    if item_folder.parent == root_path:
        if DRY_RUN and verbose:
            print(f"[DRY-RUN] Carpeta ya está en root: {item_folder}")
        return False

    try:
        if DRY_RUN:
            if verbose:
                print(f"[DRY-RUN] Mover: {item_folder} -> {destination}")
        else:
            shutil.move(str(item_folder), str(destination))
            if verbose:
                print(f"[OK] Movida: {item_folder.name} -> {destination}")
        return True
    except Exception as e:
        if verbose:
            print(f"[ERROR] Error moviendo {item_folder}: {e}")
        return False


def organize_all_items(item_folders: list[Path], root_path: Path) -> dict:
    """
    Organiza todas las carpetas de items moviéndolas al directorio raíz.

    Returns:
        dict: Estadísticas de la operación
    """
    from config import MAX_VERBOSE_ITEMS

    stats = {
        "processed": 0,
        "moved": 0,
        "skipped": 0,
        "errors": 0
    }

    print("\n" + "="*60)
    print("PASO 1: ORGANIZANDO CARPETAS DE ITEMS")
    print("="*60)

    total_items = len(item_folders)
    show_details = total_items <= MAX_VERBOSE_ITEMS

    if not show_details:
        print(f"\n[*] Organizando {total_items} carpetas (modo silencioso)...")

    for idx, item_folder in enumerate(item_folders, 1):
        stats["processed"] += 1
        result = organize_item_folder(item_folder, root_path, verbose=show_details)

        if result:
            stats["moved"] += 1
        else:
            stats["skipped"] += 1

        # Mostrar progreso cada 500 items si no es verbose
        if not show_details and idx % 500 == 0:
            print(f"[*] Progreso: {idx}/{total_items} carpetas organizadas...")

    print(f"\n[*] Items procesados: {stats['processed']}")
    print(f"[+] Movidos: {stats['moved']}")
    print(f"[-] Omitidos: {stats['skipped']}")

    return stats
