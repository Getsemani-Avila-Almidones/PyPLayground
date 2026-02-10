import os
import re
import json
import yaml
from collections import defaultdict, Counter
from config import VAULT_PATH, OUTPUT_DATA

tag_pattern = re.compile(r'#([\w\-/]+)')
link_pattern = re.compile(r'\[\[([^\]]+)\]\]')


def get_frontmatter(content):
    if content.startswith('---'):
        try:
            fm = content.split('---', 2)[1]
            return yaml.safe_load(fm)
        except:
            return None
    return None


def analyze_vault():

    print("\n====================================")
    print("ANALIZANDO VAULT OBSIDIAN")
    print("====================================")

    md_files = []
    tags_counter = Counter()
    folder_counter = Counter()
    orphan_notes = []
    no_tag_notes = []
    heavy_files = []
    links_map = defaultdict(set)
    backlinks_map = defaultdict(set)
    notes_index = []

    os.makedirs(OUTPUT_DATA, exist_ok=True)

    # ===== RECORRER VAULT SOLO UNA VEZ =====
    for root, dirs, files in os.walk(VAULT_PATH):
        for file in files:

            fullpath = os.path.join(root, file)

            # Archivos pesados
            try:
                size_mb = os.path.getsize(fullpath) / (1024 * 1024)
                if size_mb > 5:
                    heavy_files.append((file, round(size_mb, 2)))
            except:
                pass

            if not file.endswith(".md"):
                continue

            md_files.append(fullpath)

            with open(fullpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            note_name = os.path.basename(fullpath).replace(".md", "")

            # carpeta
            folder = os.path.dirname(fullpath).replace(VAULT_PATH, "")
            folder_counter[folder] += 1

            # tags
            tags = tag_pattern.findall(content)
            if not tags:
                no_tag_notes.append(note_name)
            else:
                tags_counter.update(tags)

            # links
            links = link_pattern.findall(content)
            for link in links:
                links_map[note_name].add(link)
                backlinks_map[link].add(note_name)

            # index
            notes_index.append({
                "name": note_name,
                "path": fullpath,
                "tags": tags,
                "links": links,
                "folder": folder
            })

    # ===== NOTAS HUÉRFANAS =====
    for note in links_map:
        if note not in backlinks_map:
            orphan_notes.append(note)

    # ===== DATASET =====
    links_graph = {
        "outgoing": {k: list(v) for k, v in links_map.items()},
        "backlinks": {k: list(v) for k, v in backlinks_map.items()}
    }

    # ===== GUARDAR ARCHIVOS =====
    def save(name, data):
        path = os.path.join(OUTPUT_DATA, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    save("notes_index.json", notes_index)
    save("tags_summary.json", dict(tags_counter))
    save("links_graph.json", links_graph)
    save("orphan_notes.json", orphan_notes)
    save("folders_summary.json", dict(folder_counter))
    save("heavy_files.json", heavy_files)

    # ===== REPORTE =====
    print("\nTotal de notas:", len(md_files))

    print("\n--- Carpetas ---")
    for folder, count in folder_counter.most_common(10):
        print(f"{folder}: {count} notas")

    print("\n--- Tags más usados ---")
    for tag, count in tags_counter.most_common(15):
        print(f"#{tag}: {count}")

    print("\nNotas sin tags:", len(no_tag_notes))
    print("Notas huérfanas:", len(orphan_notes))
    print("Archivos pesados:", len(heavy_files))

    print("\nDataset generado en:", OUTPUT_DATA)

    return {
        "notes_index": notes_index,
        "links_graph": links_graph,
        "tags_summary": dict(tags_counter),
        "folders_summary": dict(folder_counter),
        "orphan_notes": orphan_notes,
        "heavy_files": heavy_files
    }
