import os
import yaml
import shutil
from config import OUTPUT_APPS, OUTPUT_SERVERS, VAULT_PATH


def load_yaml_folder(folder):
    data = {}

    if not os.path.exists(folder):
        print("Carpeta no encontrada:", folder)
        return data

    for file in os.listdir(folder):
        if file.endswith(".yml"):
            path = os.path.join(folder, file)

            with open(path, encoding="utf-8") as f:
                try:
                    y = yaml.safe_load(f)
                    if y and "nombre" in y:
                        name = y["nombre"].strip()
                        data[name] = y
                        print("YAML cargado:", name)
                except Exception as e:
                    print("Error leyendo YAML:", file, e)

    print("Total YAML cargados:", len(data))
    return data


# 🔴 BÚSQUEDA INTELIGENTE DE NOTAS
def normalize(text):
    return text.lower().replace(" ", "").replace("_", "").replace("-", "")


def find_note_path(note_name):

    target = normalize(note_name)

    for root, dirs, files in os.walk(VAULT_PATH):
        for f in files:
            if not f.endswith(".md"):
                continue

            filename = f[:-3]  # quitar .md

            if normalize(filename) == target:
                path = os.path.join(root, f)
                print("Nota encontrada:", note_name, "->", path)
                return path

    print("❌ No encontrada:", note_name)
    return None


def split_frontmatter(content):

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[1], parts[2]

    return None, content


def apply_yaml_to_note(note_path, yaml_data):

    with open(note_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # backup
    backup = note_path + ".bak"
    shutil.copy2(note_path, backup)

    print("Backup creado:", backup)

    new_yaml = yaml.dump(yaml_data, allow_unicode=True, sort_keys=False)

    front, body = split_frontmatter(content)

    if front:
        print("Frontmatter existente reemplazado")
    else:
        print("Frontmatter nuevo insertado")

    new_content = f"---\n{new_yaml}---\n{body.lstrip()}"

    with open(note_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("✔ Aplicado en:", note_path)


def execute_apply():

    print("\n====================================")
    print("APLICANDO YAML A LAS NOTAS")
    print("====================================")

    apps = load_yaml_folder(OUTPUT_APPS)
    servers = load_yaml_folder(OUTPUT_SERVERS)

    all_items = {**apps, **servers}

    print("\nTotal entidades a aplicar:", len(all_items))

    applied = 0
    missing = []

    for name, yaml_data in all_items.items():

        print("\nProcesando:", name)

        path = find_note_path(name)

        if not path:
            missing.append(name)
            continue

        apply_yaml_to_note(path, yaml_data)
        applied += 1

    print("\n====================================")
    print("RESULTADO FINAL")
    print("====================================")

    print("Notas actualizadas:", applied)

    if missing:
        print("\nNo encontradas:")
        for m in missing:
            print(" -", m)
