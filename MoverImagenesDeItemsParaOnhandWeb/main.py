#!/usr/bin/env python3
"""
ORQUESTADOR PRINCIPAL - Organización de Imágenes de Items

Este script coordina todo el proceso de:
1. Escanear carpetas de items con imágenes (omitiendo carpetas SEMANA)
2. Mover las carpetas de items al directorio raíz
3. Renombrar imágenes con el formato: <NumeroDeItem>.<extension>
4. Eliminar duplicados

Estructura final: Items/<NumeroDeItem>/<NumeroDeItem>.<extension>
"""

import sys
from pathlib import Path
from config import ROOT_PATH, DRY_RUN
from modules.scanner import scan_item_folders, scan_semana_folders
from modules.organizer import organize_all_items
from modules.image_processor import process_all_images


def print_header():
    """Imprime el encabezado del programa."""
    print("\n" + "="*60)
    print("   ORGANIZADOR DE IMÁGENES DE ITEMS PARA ONHAND WEB")
    print("="*60)
    print(f"Directorio raíz: {ROOT_PATH}")
    print(f"Modo: {'DRY-RUN (sin cambios reales)' if DRY_RUN else 'PRODUCCIÓN'}")
    print("="*60)


def print_summary(scan_stats, org_stats, img_stats):
    """Imprime el resumen final de la ejecucion."""
    print("\n" + "="*60)
    print("   RESUMEN FINAL")
    print("="*60)
    print(f"\n[ESCANEO]")
    print(f"   Items encontrados: {scan_stats['total_found']}")
    print(f"   Items con imagenes: {scan_stats['with_images']}")
    print(f"   Items sin imagenes: {scan_stats['without_images']}")

    print(f"\n[ORGANIZACION]")
    print(f"   Carpetas movidas: {org_stats['moved']}")
    print(f"   Carpetas omitidas: {org_stats['skipped']}")

    print(f"\n[PROCESAMIENTO DE IMAGENES]")
    print(f"   Carpetas procesadas: {img_stats['folders_processed']}")
    print(f"   Imagenes renombradas: {img_stats['images_renamed']}")
    print(f"   Duplicados eliminados: {img_stats['duplicates_removed']}")
    print(f"   Advertencias: {img_stats['warnings']}")

    print("\n" + "="*60)
    if DRY_RUN:
        print("[!] MODO DRY-RUN: No se realizaron cambios reales")
    else:
        print("[OK] PROCESO COMPLETADO EXITOSAMENTE")
    print("="*60 + "\n")


def main():
    """Función principal que orquesta todo el proceso."""

    # Validar que el directorio raiz existe
    if not ROOT_PATH.exists():
        print(f"[ERROR] No existe el directorio raiz: {ROOT_PATH}")
        sys.exit(1)

    print_header()

    # PASO 0: Escanear carpetas SEMANA (informativo)
    print("\n" + "="*60)
    print("PASO 0: ESCANEANDO CARPETAS SEMANA (informativo)")
    print("="*60)
    semana_folders, semana_stats = scan_semana_folders(ROOT_PATH)
    print(f"[*] Carpetas SEMANA encontradas: {semana_stats['total']}")
    print(f"    Con archivos: {semana_stats['with_files']}")
    print(f"    Vacias: {semana_stats['empty']}")

    # PASO 1: Escanear carpetas de items
    print("\n" + "="*60)
    print("ESCANEANDO CARPETAS DE ITEMS")
    print("="*60)
    item_folders, scan_stats = scan_item_folders(ROOT_PATH)
    print(f"[*] Items encontrados: {scan_stats['total_found']}")
    print(f"    Con imagenes: {scan_stats['with_images']}")
    print(f"    Sin imagenes: {scan_stats['without_images']}")

    if not item_folders:
        print("\n[!] No se encontraron carpetas de items con imagenes.")
        sys.exit(0)

    # PASO 2: Organizar carpetas (mover al root)
    org_stats = organize_all_items(item_folders, ROOT_PATH)

    # PASO 3: Procesar imágenes (renombrar y eliminar duplicados)
    # Pasamos las mismas carpetas que fueron escaneadas
    img_stats = process_all_images(item_folders)

    # RESUMEN FINAL
    print_summary(scan_stats, org_stats, img_stats)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Proceso interrumpido por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)