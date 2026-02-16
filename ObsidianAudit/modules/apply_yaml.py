import os
import re
import shutil
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Tuple

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


@dataclass(frozen=True)
class FrontmatterDocument:
    """Representa el contenido completo de una nota Markdown."""

    frontmatter: Dict[str, Any]
    body: str
    eol: str


class FrontmatterParser:
    """Responsable de parsear y renderizar frontmatter de forma segura."""

    @staticmethod
    def detect_eol(text: str) -> str:
        return "\r\n" if "\r\n" in text else "\n"

    @staticmethod
    def parse(content: str) -> FrontmatterDocument:
        eol = FrontmatterParser.detect_eol(content)
        yaml_data, body = FrontmatterParser._extract_frontmatter(content)
        return FrontmatterDocument(frontmatter=yaml_data, body=body, eol=eol)

    @staticmethod
    def _extract_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
        """
        Extrae frontmatter SOLO si:
        - inicia exactamente en el byte 0 con '---\n' o '---\r\n'
        - cierra con una línea exclusiva '---'.
        """
        if not (content.startswith("---\n") or content.startswith("---\r\n")):
            return {}, content

        first_eol = "\r\n" if content.startswith("---\r\n") else "\n"
        start = len(f"---{first_eol}")
        close_marker = f"{first_eol}---{first_eol}"
        close_index = content.find(close_marker, start)

        if close_index == -1:
            return {}, content

        yaml_block = content[start:close_index]
        body_start = close_index + len(close_marker)
        body = content[body_start:]

        parsed = FrontmatterParser._safe_load_yaml(yaml_block)
        return parsed, body

    @staticmethod
    def _safe_load_yaml(yaml_block: str) -> Dict[str, Any]:
        try:
            loaded = yaml.safe_load(yaml_block)
        except yaml.YAMLError:
            return {}

        if loaded is None:
            return {}

        if isinstance(loaded, dict):
            return loaded

        return {"_legacy_frontmatter": loaded}

    @staticmethod
    def render(frontmatter: Dict[str, Any], eol: str) -> str:
        yaml_text = yaml.safe_dump(
            frontmatter,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )
        yaml_text = yaml_text.replace("\n", eol)
        return f"---{eol}{yaml_text}---{eol}"


class EntityTypeResolver:
    """Responsable de decidir el tipo de entidad destino."""

    @staticmethod
    def resolve(frontmatter: Dict[str, Any], file_path: str) -> str:
        raw_tipo = str(frontmatter.get("tipo", "")).strip().lower()
        mapped = TYPE_MAP.get(raw_tipo)
        if mapped:
            return mapped

        lowered_path = file_path.lower()
        if "incidente" in lowered_path:
            return "incident"
        if "server" in lowered_path or "servidor" in lowered_path:
            return "server"
        return "service"


class YamlNormalizer:
    """Responsable de normalizar frontmatter al modelo CMDB objetivo."""

    def build(self, entity_type: str, file_title: str, current: Dict[str, Any]) -> Dict[str, Any]:
        slug = self._slugify(file_title)

        if entity_type == "server":
            return self._build_server(slug, file_title, current)
        if entity_type == "incident":
            return self._build_incident(slug, current)
        return self._build_service(slug, file_title, current)

    @staticmethod
    def _slugify(text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text)
        ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
        lowered = ascii_only.lower()
        slug = re.sub(r"[^a-z0-9]+", "_", lowered).strip("_")
        return slug or "item"

    @staticmethod
    def _safe_dict(value: Any) -> Dict[str, Any]:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _build_server(slug: str, file_title: str, current: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": f"srv_{slug}",
            "tipo": "servidor",
            "nombre": current.get("nombre", file_title),
            "estado": current.get("estado", "productivo"),
            "criticidad": current.get("criticidad", "media"),
            "responsable": current.get("responsable", "infraestructura"),
            "tags": current.get("tags", ["servidor"]),
        }

    @staticmethod
    def _build_incident(slug: str, current: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": f"inc_{slug}",
            "tipo": "incidente",
            "afecta": current.get("afecta", []),
            "estado": current.get("estado", "cerrado"),
            "criticidad": current.get("criticidad", "media"),
            "tags": current.get("tags", ["incidente"]),
        }

    def _build_service(self, slug: str, file_title: str, current: Dict[str, Any]) -> Dict[str, Any]:
        seguridad = self._safe_dict(current.get("seguridad"))

        return {
            "id": f"svc_{slug}",
            "tipo": "servicio",
            "nombre": current.get("nombre", file_title),
            "estado": current.get("estado", "productivo"),
            "criticidad": current.get("criticidad", "media"),
            "responsable": current.get("responsable", "aplicaciones"),
            "corre_en": current.get("corre_en", []),
            "depende_de": current.get("depende_de", []),
            "seguridad": {
                "autenticacion": seguridad.get("autenticacion", False),
                "cifrado": seguridad.get("cifrado", False),
                "acceso_externo": seguridad.get("acceso_externo", False),
            },
            "tags": current.get("tags", []),
        }


class MarkdownYamlMigrator:
    """Orquesta migración segura de una nota markdown."""

    def __init__(self, parser: FrontmatterParser, resolver: EntityTypeResolver, normalizer: YamlNormalizer):
        self._parser = parser
        self._resolver = resolver
        self._normalizer = normalizer

    def migrate_file(self, md_path: str) -> bool:
        original = self._read_file(md_path)
        parsed = self._parser.parse(original)

        file_title = os.path.splitext(os.path.basename(md_path))[0]
        entity_type = self._resolver.resolve(parsed.frontmatter, md_path)
        target_frontmatter = self._normalizer.build(entity_type, file_title, parsed.frontmatter)

        new_content = f"{self._parser.render(target_frontmatter, parsed.eol)}{parsed.body}"
        if new_content == original:
            return False

        self._create_backup(md_path)
        self._write_file(md_path, new_content)
        return True

    @staticmethod
    def _read_file(path: str) -> str:
        with open(path, "r", encoding="utf-8", newline="") as file:
            return file.read()

    @staticmethod
    def _write_file(path: str, content: str) -> None:
        with open(path, "w", encoding="utf-8", newline="") as file:
            file.write(content)

    @staticmethod
    def _create_backup(path: str) -> None:
        shutil.copy2(path, f"{path}.bak")


class VaultScanner:
    """Responsable de descubrir archivos markdown del vault."""

    @staticmethod
    def iter_markdown_files(vault_path: str) -> Iterable[str]:
        for root, _, files in os.walk(vault_path):
            for file_name in files:
                if file_name.lower().endswith(".md"):
                    yield os.path.join(root, file_name)


def execute_apply() -> None:
    print("\n====================================")
    print("MIGRACION YAML FRONTMATTER")
    print("====================================")

    migrator = MarkdownYamlMigrator(
        parser=FrontmatterParser(),
        resolver=EntityTypeResolver(),
        normalizer=YamlNormalizer(),
    )

    updated = 0
    errors = []

    for file_path in VaultScanner.iter_markdown_files(VAULT_PATH):
        try:
            if migrator.migrate_file(file_path):
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
