import os
import re
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, List

# =========================
# CONFIGURACIÓN PRINCIPAL
# =========================
VAULT_PATH = r"C:\Users\21596\Documents\Obsidian\AlmexVault"  # <-- CAMBIA ESTO
APPS_FOLDER_REL = r"Application\Fichas Tecnicas Aplicaciones"  # carpeta relativa dentro del vault

OUTPUT_FOLDER_REL = r"_yaml_sugerido\apps"  # se creará dentro del vault
DRY_RUN = True  # True = no toca nada, solo genera yml sugeridos (recomendado)
OVERWRITE_YML = True  # si ya existe el .yml sugerido, lo reemplaza

# =========================
# TEMPLATE (AJÚSTALO A TU FICHA TÉCNICA)
# - Deja valores "" si son manuales.
# - Puedes poner valores default.
# =========================
TEMPLATE: Dict[str, object] = {
    "tipo": "aplicacion",
    "nombre": "",                 # se intenta inferir del nombre del archivo
    "area": "",                   # ejemplo: Finanzas
    "propietario": "",            # ejemplo: Dir. General / Planeación
    "responsable_ti": "",         # ejemplo: Sistemas / Getsemani / Omar
    "criticidad": "",             # baja|media|alta|critica
    "ambiente": "",               # PROD|TEST|DEV
    "tecnologia": "",             # Oracle|Laravel|APEX|Windows App|etc.
    "proveedor": "",              # Interno|ConPaq|Tercero
    "url": "",
    "servidores": [],             # lista
    "bases_datos": [],            # lista
    "integraciones": [],          # lista
    "tags": ["activo", "app"],    # base mínima
}

# =========================
# PATRONES (AJÚSTALOS A CÓMO ESCRIBES TU FICHA)
# Ejemplos que detecta:
#   Área: Finanzas
#   Responsable TI: Getsemani
#   Criticidad: Alta
# =========================
FIELD_PATTERNS: Dict[str, List[re.Pattern]] = {
    "area": [
        re.compile(r"^\s*(?:Área|Area)\s*:\s*(.+)\s*$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^\s*Departamento\s*:\s*(.+)\s*$", re.IGNORECASE | re.MULTILINE),
    ],
    "responsable_ti": [
        re.compile(r"^\s*Responsable\s*TI\s*:\s*(.+)\s*$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^\s*Dueño\s*TI\s*:\s*(.+)\s*$", re.IGNORECASE | re.MULTILINE),
    ],
    "criticidad": [
        re.compile(r"^\s*Criticidad\s*:\s*(.+)\s*$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^\s*Relevancia\s*:\s*(.+)\s*$", re.IGNORECASE | re.MULTILINE),
    ],
    "tecnologia": [
        re.compile(r"^\s*(?:Tecnología|Tecnologia)\s*:\s*(.+)\s*$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^\s*Stack\s*:\s*(.+)\s*$", re.IGNORECASE | re.MULTILINE),
    ],
    "url": [
        re.compile(r"^\s*URL\s*:\s*(.+)\s*$", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^\s*Enlace\s*:\s*(.+)\s*$", re.IGNORECASE | re.MULTILINE),
    ],
}


# =========================
# UTILIDADES
# =========================
FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)

def has_frontmatter(md_text: str) -> bool:
    return bool(FRONTMATTER_RE.match(md_text))

def infer_name_from_filename(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0].strip()

def normalize_scalar(value: str) -> str:
    return value.strip().strip('"').strip("'")

def extract_field(md_text: str, key: str) -> Optional[str]:
    patterns = FIELD_PATTERNS.get(key, [])
    for p in patterns:
        m = p.search(md_text)
        if m:
            return normalize_scalar(m.group(1))
    return None

def to_yaml(data: Dict[str, object], indent: int = 0) -> str:
    # YAML simple (sin depender de PyYAML)
    # Maneja: str, list[str], dict simple
    lines = []
    pad = " " * indent

    for k, v in data.items():
        if isinstance(v, list):
            if len(v) == 0:
                lines.append(f"{pad}{k}: []")
            else:
                lines.append(f"{pad}{k}:")
                for item in v:
                    if isinstance(item, str):
                        lines.append(f"{pad}- {item}")
                    else:
                        lines.append(f"{pad}- {str(item)}")
        elif isinstance(v, dict):
            lines.append(f"{pad}{k}:")
            lines.append(to_yaml(v, indent=indent + 2))
        else:
            # strings / scalars
            if v is None:
                v = ""
            if isinstance(v, str):
                # si tiene ":" o "#", mejor comillas
                if any(ch in v for ch in [":", "#", "{", "}", "[", "]"]):
                    v_out = '"' + v.replace('"', '\\"') + '"'
                else:
                    v_out = v
            else:
                v_out = str(v)
            lines.append(f"{pad}{k}: {v_out}")

    return "\n".join(lines)

@dataclass
class NoteResult:
    file_path: str
    yaml_path: str
    used_fields: List[str]
    missing_fields: List[str]


def build_yaml_for_note(md_text: str, note_name: str) -> Tuple[Dict[str, object], List[str], List[str]]:
    y = dict(TEMPLATE)  # shallow copy

    # defaults
    y["nombre"] = note_name

    used = []
    missing = []

    for key in y.keys():
        # autollenar solo si es string vacío
        if isinstance(y[key], str) and y[key] == "":
            extracted = extract_field(md_text, key)
            if extracted:
                y[key] = extracted
                used.append(key)

    # tags extra sugeridos por área/criticidad (muy básico v1)
    tags = set(y.get("tags", []))
    if isinstance(y.get("area"), str) and y["area"].strip():
        tags.add(y["area"].strip().lower().replace(" ", "_"))
    if isinstance(y.get("criticidad"), str) and y["criticidad"].strip():
        tags.add("crit_" + y["criticidad"].strip().lower().replace(" ", "_"))
    y["tags"] = sorted(tags)

    # missing fields (strings vacíos importantes)
    important = ["area", "responsable_ti", "criticidad", "tecnologia", "url"]
    for k in important:
        if isinstance(y.get(k), str) and not y[k].strip():
            missing.append(k)

    return y, used, missing


def main():
    apps_folder = os.path.join(VAULT_PATH, APPS_FOLDER_REL)
    out_folder = os.path.join(VAULT_PATH, OUTPUT_FOLDER_REL)

    if not os.path.isdir(apps_folder):
        raise SystemExit(f"❌ No existe la carpeta de apps: {apps_folder}")

    os.makedirs(out_folder, exist_ok=True)

    results: List[NoteResult] = []
    total = 0
    skipped_has_frontmatter = 0

    for root, _, files in os.walk(apps_folder):
        for f in files:
            if not f.lower().endswith(".md"):
                continue

            total += 1
            md_path = os.path.join(root, f)

            with open(md_path, "r", encoding="utf-8", errors="ignore") as fh:
                md_text = fh.read()

            if has_frontmatter(md_text):
                skipped_has_frontmatter += 1
                continue

            note_name = infer_name_from_filename(md_path)
            yaml_data, used_fields, missing_fields = build_yaml_for_note(md_text, note_name)

            yaml_text = to_yaml(yaml_data)
            yaml_text = f"---\n{yaml_text}\n---\n"

            # nombre .yml sugerido
            yml_file = note_name.replace("/", "_").replace("\\", "_") + ".yml"
            yaml_path = os.path.join(out_folder, yml_file)

            if os.path.exists(yaml_path) and not OVERWRITE_YML:
                continue

            if not DRY_RUN:
                with open(yaml_path, "w", encoding="utf-8") as out:
                    out.write(yaml_text)
            else:
                # en dry-run igual lo escribimos para que lo uses; si quieres que no escriba nada, lo quitas
                with open(yaml_path, "w", encoding="utf-8") as out:
                    out.write(yaml_text)

            results.append(NoteResult(md_path, yaml_path, used_fields, missing_fields))

    # ===== REPORTE =====
    print("\n=========== OBSIDIAN APPS → YAML (v1) ===========")
    print(f"Vault: {VAULT_PATH}")
    print(f"Carpeta Apps: {VAULT_PATH}\\{APPS_FOLDER_REL}")
    print(f"Salida: {VAULT_PATH}\\{OUTPUT_FOLDER_REL}")
    print(f"Total notas .md encontradas: {total}")
    print(f"Notas con frontmatter (saltadas): {skipped_has_frontmatter}")
    print(f"Notas sin frontmatter (procesadas): {len(results)}")

    if results:
        print("\n--- Detalle (primeras 20) ---")
        for r in results[:20]:
            print(f"\n• {os.path.basename(r.file_path)}")
            print(f"  YAML: {os.path.basename(r.yaml_path)}")
            print(f"  Autollenado: {', '.join(r.used_fields) if r.used_fields else '(nada)'}")
            print(f"  Faltante: {', '.join(r.missing_fields) if r.missing_fields else '(ok)'}")

        # resumen de campos más faltantes
        missing_counter = {}
        for r in results:
            for m in r.missing_fields:
                missing_counter[m] = missing_counter.get(m, 0) + 1

        if missing_counter:
            print("\n--- Campos más faltantes ---")
            for k, v in sorted(missing_counter.items(), key=lambda x: x[1], reverse=True):
                print(f"{k}: {v}")

    print("\n✅ Listo. (Si quieres que inserte el YAML dentro de cada nota .md, lo hacemos en v1.1)")
    print("=========== FIN ===========\n")
