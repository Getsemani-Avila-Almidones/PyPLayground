import os
import re
import yaml
from collections import defaultdict, Counter

# === CONFIGURA TU VAULT AQUÍ ===
VAULT_PATH = r"C:\Users\21596\Documents\Obsidian\GetsemaniAvila-Vault"

md_files = []
tags_counter = Counter()
folder_counter = Counter()
orphan_notes = []
no_tag_notes = []
heavy_files = []
links_map = defaultdict(set)
backlinks_map = defaultdict(set)

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

# ===== RECORRER VAULT =====
for root, dirs, files in os.walk(VAULT_PATH):
    for file in files:
        fullpath = os.path.join(root, file)

        # Archivos pesados
        size_mb = os.path.getsize(fullpath) / (1024 * 1024)
        if size_mb > 5:
            heavy_files.append((file, round(size_mb, 2)))

        if file.endswith(".md"):
            md_files.append(fullpath)

# ===== ANALIZAR MARKDOWN =====
for file in md_files:
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    note_name = os.path.basename(file).replace(".md", "")

    # carpetas
    folder = os.path.dirname(file).replace(VAULT_PATH, "")
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

# ===== NOTAS HUÉRFANAS =====
for note in links_map:
    if note not in backlinks_map:
        orphan_notes.append(note)

# ===== REPORTE =====
print("\n=========== REPORTE OBSIDIAN ===========")

print("\nTotal de notas:", len(md_files))

print("\n--- Carpetas ---")
for folder, count in folder_counter.most_common(15):
    print(f"{folder}: {count} notas")

print("\n--- Tags más usados ---")
for tag, count in tags_counter.most_common(20):
    print(f"#{tag}: {count}")

print("\n--- Notas sin tags ---")
print(len(no_tag_notes))
for n in no_tag_notes[:20]:
    print("-", n)

print("\n--- Notas huérfanas (nadie las referencia) ---")
print(len(orphan_notes))
for n in orphan_notes[:20]:
    print("-", n)

print("\n--- Archivos pesados (>5MB) ---")
for f, s in heavy_files:
    print(f"{f} - {s} MB")

print("\n=========== FIN REPORTE ===========")
