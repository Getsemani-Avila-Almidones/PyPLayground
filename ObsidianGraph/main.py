import os
import re
import yaml

from graphviz import Digra`ph
from modules.entity_classifier import detect_type

from config import OUTPUT_DATA, OUTPUT_APPS, VAULT_PATH

VAULT = VAULT_PATH

graph = Digraph("Infraestructura", format="png")
graph.attr(rankdir="LR", splines="ortho")

def clean_link(text):
    if not text:
        return None
    match = re.search(r"\[\[(.*?)\]\]", str(text))
    return match.group(1) if match else None

for root, _, files in os.walk(VAULT):
    for file in files:
        if not file.endswith(".md"):
            continue

        path = os.path.join(root, file)

        with open(path, encoding="utf-8") as f:
            content = f.read()

        if not content.startswith("---"):
            continue

        try:
            yaml_block = content.split("---")[1]
            data = yaml.safe_load(yaml_block)
        except:
            continue

        if not isinstance(data, dict):
            continue

        source = file.replace(".md","")

        # nodo principal
        graph.node(source, shape="box", style="filled", fillcolor="#cce5ff")

        # depende_de
        if "depende_de" in data:
            for dep in data["depende_de"]:
                target = clean_link(dep)
                if target:
                    graph.node(target, shape="box")
                    graph.edge(source, target, label="depende")

        # corre_en
        if "corre_en" in data:
            for srv in data["corre_en"]:
                target = clean_link(srv)
                if target:
                    graph.node(target, shape="component", fillcolor="#ffe6cc", style="filled")
                    graph.edge(source, target, label="corre en")

graph.render("mapa_infraestructura", view=True)
