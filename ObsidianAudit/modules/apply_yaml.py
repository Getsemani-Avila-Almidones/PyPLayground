import os
import re
import shutil
import unicodedata
from typing import Any, Dict, Optional, Tuple

import yaml

from config import VAULT_PATH

TYPE_MAP = {
    "aplicacion": "service",
    "servicio": "service",
    "server": "server",
    "servidor": "server",
    "incidente": "incident",
    "incident": "incident",
}


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", lowered).strip("_")
    return slug or "item"


def detect_eol(text: str) -> str:
    if "\r\n" in text:
        return "\r\n"
    return "\n"


def parse_frontmatter(content: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Parse frontmatter only when it starts at byte 0 and closes with a dedicated marker line.
    Returns (yaml_dict_or_none, body_exact_text).
    """
    if not (content.startswith("---\n") or content.startswith("---\r\n")):
        return None, content

    first_eol = "\r\n" if content.startswith("---\r\n") else "\n"
    start = len(f"---{first_eol}")
    closing_marker = f"{first_eol}---{first_eol}"
    closing_idx = content.find(closing_marker, start)

    if closing_idx == -1:
        return None, content

    yaml_block = content[start:closing_idx]
    body_start = closing_idx + len(closing_marker)
    body = content[body_start:]

    try:
        parsed = yaml.safe_load(yaml_block)
    except yaml.YAMLError:
        parsed = None

    if parsed is None:
        parsed = {}

    if not isinstance(parsed, dict):
        parsed = {"_legacy_frontmatter": parsed}

    return parsed, body


def infer_entity_type(frontmatter: Dict[str, Any], file_path: str) -> str:
    raw_tipo = str(frontmatter.get("tipo", "")).strip().lower()
    if raw_tipo in TYPE_MAP:
        return TYPE_MAP[raw_tipo]

    lowered_path = file_path.lower()
    if "incidente" in lowered_path:
        return "incident"
    if "server" in lowered_path or "servidor" in lowered_path:
        return "server"
    return "service"


def build_target_yaml(entity_type: str, title: str, slug: str, current: Dict[str, Any]) -> Dict[str, Any]:
    criticidad = current.get("criticidad", "media")

    if entity_type == "server":
        return {
            "id": f"srv_{slug}",
            "tipo": "servidor",
            "nombre": current.get("nombre", title),
            "estado": current.get("estado", "productivo"),
            "criticidad": criticidad,
            "responsable": current.get("responsable", "infraestructura"),
            "tags": current.get("tags", ["servidor"]),
        }

    if entity_type == "incident":
        return {
            "id": f"inc_{slug}",
            "tipo": "incidente",
            "afecta": current.get("afecta", []),
            "estado": current.get("estado", "cerrado"),
            "criticidad": criticidad,
            "tags": current.get("tags", ["incidente"]),
        }

    return {
        "id": f"svc_{slug}",
        "tipo": "servicio",
        "nombre": current.get("nombre", title),
        "estado": current.get("estado", "productivo"),
        "criticidad": criticidad,
        "responsable": current.get("responsable", "aplicaciones"),
        "corre_en": current.get("corre_en", []),
        "depende_de": current.get("depende_de", []),
        "seguridad": {
            "autenticacion": current.get("seguridad", {}).get("autenticacion", False)
            if isinstance(current.get("seguridad"), dict)
            else False,
            "cifrado": current.get("seguridad", {}).get("cifrado", False)
            if isinstance(current.get("seguridad"), dict)
            else False,
            "acceso_externo": current.get("seguridad", {}).get("acceso_externo", False)
            if isinstance(current.get("seguridad"), dict)
            else False,
        },
        "tags": current.get("tags", []),
    }


def render_frontmatter(data: Dict[str, Any], eol: str) -> str:
    yaml_text = yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )
    yaml_text = yaml_text.replace("\n", eol)
    return f"---{eol}{yaml_text}---{eol}"


def process_markdown_file(md_path: str) -> bool:
    with open(md_path, "r", encoding="utf-8", newline="") as f:
        original = f.read()

    eol = detect_eol(original)
    current_frontmatter, body = parse_frontmatter(original)
    current_frontmatter = current_frontmatter or {}

    filename = os.path.splitext(os.path.basename(md_path))[0]
    slug = slugify(filename)
    entity_type = infer_entity_type(current_frontmatter, md_path)
    target = build_target_yaml(entity_type, filename, slug, current_frontmatter)

    new_content = f"{render_frontmatter(target, eol)}{body}"

    if new_content == original:
        return False

    backup_path = f"{md_path}.bak"
    shutil.copy2(md_path, backup_path)

    with open(md_path, "w", encoding="utf-8", newline="") as f:
        f.write(new_content)

    return True


def execute_apply() -> None:
    print("\n====================================")
    print("MIGRACION YAML FRONTMATTER")
    print("====================================")

    updated = 0
    errors = []

    for root, _, files in os.walk(VAULT_PATH):
        for name in files:
            if not name.lower().endswith(".md"):
                continue

            file_path = os.path.join(root, name)
            try:
                changed = process_markdown_file(file_path)
                if changed:
                    updated += 1
                    print(f"✔ Actualizado: {file_path}")
            except Exception as exc:
                errors.append((file_path, str(exc)))
                print(f"❌ Error en {file_path}: {exc}")

    print("\n====================================")
    print("RESULTADO")
    print("====================================")
    print(f"Notas actualizadas: {updated}")

    if errors:
        print("\nArchivos con error:")
        for path, err in errors:
            print(f" - {path}: {err}")
