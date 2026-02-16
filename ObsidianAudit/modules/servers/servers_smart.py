import os
import json

import yaml
from modules.entity_classifier import detect_type
from config import OUTPUT_DATA, OUTPUT_SERVERS

def load_dataset():
    with open(os.path.join(OUTPUT_DATA, "notes_index.json"), encoding="utf-8") as f:
        notes = json.load(f)

    with open(os.path.join(OUTPUT_DATA, "links_graph.json"), encoding="utf-8") as f:
        links = json.load(f)

    return notes, links

def is_application(name):
    return not name.lower().startswith("inc")

def generate_server_yaml(server_name, links_graph):

    apps = []
    incidentes = []

    backlinks = links_graph["backlinks"].get(server_name, [])

    for ref in backlinks:
        if ref.lower().startswith("inc"):
            incidentes.append(ref)
        else:
            apps.append(ref)

    impacto = "alto" if len(apps) >= 3 else "medio"

    data = {
        "tipo": "servidor",
        "nombre": server_name,
        "aplicaciones_hosteadas": apps,
        "incidentes_relacionados": incidentes,
        "impacto_negocio": impacto,
        "tags": ["activo", "servidor"] + (["critico"] if impacto == "alto" else [])
    }

    return data

def to_yaml(data):
    return yaml.dump(
        data,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False
    )

def execute(dataset=None):

    print("\nGENERANDO YAML INTELIGENTE DE SERVIDORES")

    notes, links = load_dataset()

    os.makedirs(OUTPUT_SERVERS, exist_ok=True)

    for note in notes:
        name = note["name"]

        # Detectar servidores por carpeta
        tipo = detect_type(note["name"], note["folder"], "")
        if tipo != "servidor":
            continue

        yaml_data = generate_server_yaml(name, links)
        yaml_text = to_yaml(yaml_data)

        out = os.path.join(OUTPUT_SERVERS, name + ".yml")
        with open(out, "w", encoding="utf-8") as f:
            f.write(yaml_text)

        print("Servidor analizado:", name)
