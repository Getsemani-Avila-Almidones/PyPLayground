from pathlib import Path
import os

ROOT_PATH = Path(r"C:\Users\21596\Documents\Dev\rptOnHandWeb\assets\items")  # cambia esta ruta


def folder_has_files(folder: Path) -> bool:
    for _, _, files in os.walk(folder):
        if files:
            return True
    return False


def find_semana_folders(root_path: Path):
    total = 0
    with_files = 0
    empty = 0

    for dirpath, dirnames, _ in os.walk(root_path):
        current_dir = Path(dirpath)

        if current_dir.name.startswith("SEMANA"):
            total += 1
            if folder_has_files(current_dir):
                with_files += 1
                print(f"[CON ARCHIVOS] {current_dir}")
            else:
                empty += 1
                print(f"[VACÍA] {current_dir}")

    print("\n====================")
    print(f"Carpetas SEMANA encontradas: {total}")
    print(f"Con archivos: {with_files}")
    print(f"Vacías: {empty}")
    print("====================")


if __name__ == "__main__":
    if not ROOT_PATH.exists():
        raise FileNotFoundError(f"No existe la ruta: {ROOT_PATH}")

    find_semana_folders(ROOT_PATH)