import os
import json

import yaml
from modules.entity_classifier import detect_type
from config import OUTPUT_DATA, OUTPUT_APPS

def load_dataset():
    with open(os.path.join(OUTPUT_DATA, "notes_index.json"), encoding="utf-8") as f:
        notes = json.load(f)

    with open(os.path.join(OUTPUT_DATA, "links_graph.json"), encoding="utf-8") as f:
        links = json.load(f)

    return notes, links

def is_server(name):
    name = name.lower()
    return name.startswith("dc") or "srv" in name or "server" in name

def is_incident(name):
    name = name.lower()
    return name.startswith("inc") or "incidente" in name

def is_process(name):
    return "proceso" in name.lower() or "procedimiento" in name.lower()

def generate_app_yaml(app_name, links_graph):
    outgoing = links_graph["outgoing"].get(app_name, [])
    backlinks = links_graph["backlinks"].get(app_name, [])

    servidores = []
    incidentes = []
    procesos = []

    # Detectar dependencias por backlinks
    for ref in backlinks:
        if is_server(ref):
            servidores.append(ref)
        elif is_incident(ref):
            incidentes.append(ref)
        elif is_process(ref):
            procesos.append(ref)

    criticidad = "alta" if len(incidentes) > 0 else "media"

    data = {
        "tipo": "aplicacion",
        "nombre": app_name,
        "criticidad": criticidad,
        "servidores": servidores,
        "procesos_relacionados": procesos,
        "incidentes_relacionados": incidentes,
        "tags": ["activo", "app"] + (["critico"] if criticidad == "alta" else [])
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

    print("\nGENERANDO YAML INTELIGENTE DE APLICACIONES")

    notes, links = load_dataset()

    os.makedirs(OUTPUT_APPS, exist_ok=True)

    for note in notes:
        name = note["name"]

        tipo = detect_type(note["name"], note["folder"], "")

        if tipo != "aplicacion":
            continue

        yaml_data = generate_app_yaml(name, links)
        yaml_text = to_yaml(yaml_data)

        out = os.path.join(OUTPUT_APPS, name + ".yml")
        with open(out, "w", encoding="utf-8") as f:
            f.write(yaml_text)

        print("App analizada:", name)
