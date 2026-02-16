import os
import json
import yaml
from collections import defaultdict
from config import OUTPUT_DATA, OUTPUT_APPS, OUTPUT_SERVERS

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def load_json(name):
    with open(os.path.join(OUTPUT_DATA, name), encoding="utf-8") as f:
        return json.load(f)

def load_yaml_folder(folder):
    data = []
    if not os.path.exists(folder):
        return data

    for file in os.listdir(folder):
        if file.endswith(".yml"):
            with open(os.path.join(folder, file), encoding="utf-8") as f:
                try:
                    y = yaml.safe_load(f)
                    if y:
                        data.append(y)
                except:
                    pass
    return data

def execute_dashboard():

    clear()

    print("==========================================")
    print("        OBSIDIAN TI KNOWLEDGE DASHBOARD")
    print("==========================================\n")

    notes = load_json("notes_index.json")
    links = load_json("links_graph.json")
    tags = load_json("tags_summary.json")
    orphan = load_json("orphan_notes.json")

    apps = load_yaml_folder(OUTPUT_APPS)
    servers = load_yaml_folder(OUTPUT_SERVERS)

    # --- RESUMEN GENERAL ---
    print("RESUMEN GENERAL")
    print("------------------------------------------")
    print("Notas totales:", len(notes))
    print("Aplicaciones detectadas:", len(apps))
    print("Servidores detectados:", len(servers))
    print("Notas huérfanas:", len(orphan))
    print("Tags únicos:", len(tags))
    print()

    # --- DEPENDENCIAS ---
    print("DEPENDENCIAS DETECTADAS")
    print("------------------------------------------")

    total_rel = 0
    for app in apps:
        total_rel += len(app.get("servidores", []))

    print("Relaciones App → Servidor:", total_rel)

    # --- SERVIDORES SIN APPS ---
    sin_apps = []
    for s in servers:
        if len(s.get("aplicaciones_hosteadas", [])) == 0:
            sin_apps.append(s["nombre"])

    print("Servidores sin aplicaciones:", len(sin_apps))
    for s in sin_apps[:10]:
        print("  -", s)
    print()

    # --- APPS SIN SERVIDOR ---
    apps_sin_srv = []
    for app in apps:
        if len(app.get("servidores", [])) == 0:
            apps_sin_srv.append(app["nombre"])

    print("Aplicaciones sin servidor:", len(apps_sin_srv))
    for a in apps_sin_srv[:10]:
        print("  -", a)
    print()

    # --- INCIDENTES ---
    total_inc = 0
    for app in apps:
        total_inc += len(app.get("incidentes_relacionados", []))

    print("Incidentes relacionados con aplicaciones:", total_inc)
    print()

    # --- RIESGO ---
    print("ANÁLISIS DE RIESGO")
    print("------------------------------------------")

    riesgo_alto = []
    for s in servers:
        if s.get("impacto_negocio") == "alto":
            riesgo_alto.append(s["nombre"])

    print("Servidores de alto impacto:", len(riesgo_alto))
    for r in riesgo_alto[:10]:
        print("  -", r)

    print()

    # --- HALLAZGOS ---
    print("HALLAZGOS AUTOMÁTICOS")
    print("------------------------------------------")

    if len(orphan) > 20:
        print("⚠️  Tienes demasiadas notas huérfanas (conocimiento perdido)")

    if len(apps_sin_srv) > 5:
        print("⚠️  Hay aplicaciones sin infraestructura definida")

    if len(sin_apps) > 5:
        print("⚠️  Hay servidores sin aplicaciones conocidas")

    if len(tags) < 5:
        print("⚠️  Tu sistema de tags es casi inexistente")

    print("\n==========================================\n")
