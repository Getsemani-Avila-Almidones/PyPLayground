from pathlib import Path
from config import DRY_RUN
from utils.helpers import get_images_in_folder, file_hash


def process_item_images(item_folder: Path) -> dict:
    """
    Procesa las imágenes de una carpeta de item:
    1. Renombra la imagen principal a <NombreItem>.<extension>
    2. Elimina duplicados

    Returns:
        dict: Estadísticas del procesamiento
    """
    stats = {
        "renamed": False,
        "duplicates_removed": 0,
        "warnings": 0
    }

    images = get_images_in_folder(item_folder)

    if not images:
        return stats

    # Buscar si ya existe una imagen con el nombre correcto
    main_image = None
    for img in images:
        expected_name = f"{item_folder.name}{img.suffix.lower()}"
        if img.name == expected_name:
            main_image = img
            break

    # Si no existe, renombrar la primera imagen encontrada
    if main_image is None:
        source = images[0]
        destination = item_folder / f"{item_folder.name}{source.suffix.lower()}"

        if source.resolve() != destination.resolve():
            if DRY_RUN:
                print(f"  [DRY-RUN] Renombrar: {source.name} -> {destination.name}")
            else:
                if destination.exists():
                    destination.unlink()
                source.rename(destination)
                print(f"  [OK] Renombrada: {source.name} -> {destination.name}")

            stats["renamed"] = True

        # En DRY-RUN, usar source para el hash; en producción usar destination
        main_image = source if DRY_RUN else destination

    # Refrescar la lista de imágenes después del renombrado
    if not DRY_RUN:
        images = get_images_in_folder(item_folder)

    # Eliminar duplicados basándose en hash
    main_hash = file_hash(main_image)

    for img in images:
        if img.resolve() == main_image.resolve():
            continue

        try:
            if file_hash(img) == main_hash:
                if DRY_RUN:
                    print(f"  [DRY-RUN] Eliminar duplicado: {img.name}")
                else:
                    img.unlink()
                    print(f"  [OK] Eliminado duplicado: {img.name}")
                stats["duplicates_removed"] += 1
            else:
                print(f"  [!] Imagen diferente encontrada (no eliminada): {img.name}")
                stats["warnings"] += 1
        except FileNotFoundError:
            continue

    return stats


def process_item_images_silent(item_folder: Path) -> dict:
    """
    Versión silenciosa de process_item_images (sin prints).
    Procesa las imágenes de una carpeta de item sin mostrar detalles.

    Returns:
        dict: Estadísticas del procesamiento
    """
    stats = {
        "renamed": False,
        "duplicates_removed": 0,
        "warnings": 0
    }

    images = get_images_in_folder(item_folder)

    if not images:
        return stats

    # Buscar si ya existe una imagen con el nombre correcto
    main_image = None
    for img in images:
        expected_name = f"{item_folder.name}{img.suffix.lower()}"
        if img.name == expected_name:
            main_image = img
            break

    # Si no existe, renombrar la primera imagen encontrada
    if main_image is None:
        source = images[0]
        destination = item_folder / f"{item_folder.name}{source.suffix.lower()}"

        if source.resolve() != destination.resolve():
            if not DRY_RUN:
                if destination.exists():
                    destination.unlink()
                source.rename(destination)
            stats["renamed"] = True

        main_image = destination if not DRY_RUN else source

    # Refrescar la lista de imágenes después del renombrado
    if not DRY_RUN:
        images = get_images_in_folder(item_folder)

    # Eliminar duplicados basándose en hash
    try:
        main_hash = file_hash(main_image)

        for img in images:
            if img.resolve() == main_image.resolve():
                continue

            try:
                if file_hash(img) == main_hash:
                    if not DRY_RUN:
                        img.unlink()
                    stats["duplicates_removed"] += 1
                else:
                    stats["warnings"] += 1
            except FileNotFoundError:
                continue
    except Exception:
        # Si hay error al calcular hash, solo marcar warning
        stats["warnings"] += 1

    return stats


def process_all_images(item_folders: list[Path]) -> dict:
    """
    Procesa las imágenes de todas las carpetas de items proporcionadas.

    Args:
        item_folders: Lista de carpetas de items a procesar

    Returns:
        dict: Estadísticas globales del procesamiento
    """
    from config import MAX_VERBOSE_ITEMS

    global_stats = {
        "folders_processed": 0,
        "images_renamed": 0,
        "duplicates_removed": 0,
        "warnings": 0,
        "folders_skipped": 0
    }

    print("\n" + "="*60)
    print("PASO 2: PROCESANDO IMÁGENES")
    print("="*60)

    if not item_folders:
        print("\n[!] No hay carpetas de items para procesar")
        return global_stats

    total_items = len(item_folders)
    show_details = total_items <= MAX_VERBOSE_ITEMS

    if not show_details:
        print(f"\n[*] Procesando {total_items} carpetas (mostrando solo primeras {MAX_VERBOSE_ITEMS})...")

    for idx, item_folder in enumerate(sorted(item_folders, key=lambda x: x.name), 1):
        images = get_images_in_folder(item_folder)

        if not images:
            global_stats["folders_skipped"] += 1
            continue

        # Mostrar detalles solo para las primeras MAX_VERBOSE_ITEMS carpetas
        verbose = show_details or idx <= MAX_VERBOSE_ITEMS

        if verbose:
            print(f"\n[{idx}/{total_items}] Procesando: {item_folder.name}")

        stats = process_item_images(item_folder) if verbose else process_item_images_silent(item_folder)

        global_stats["folders_processed"] += 1
        if stats["renamed"]:
            global_stats["images_renamed"] += 1
        global_stats["duplicates_removed"] += stats["duplicates_removed"]
        global_stats["warnings"] += stats["warnings"]

        # Mostrar progreso cada 500 items si no es verbose
        if not show_details and idx % 500 == 0:
            print(f"[*] Progreso: {idx}/{total_items} carpetas procesadas...")

    print(f"\n[*] Carpetas procesadas: {global_stats['folders_processed']}")
    print(f"[+] Imagenes renombradas: {global_stats['images_renamed']}")
    print(f"[+] Duplicados eliminados: {global_stats['duplicates_removed']}")
    print(f"[!] Advertencias: {global_stats['warnings']}")
    print(f"[-] Carpetas omitidas (sin imagenes): {global_stats['folders_skipped']}")

    return global_stats
