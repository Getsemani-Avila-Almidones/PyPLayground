import os
import re

VAULT_PATH = r"C:\Users\21596\Documents\Obsidian\AlmexVault"  # <-- CAMBIA ESTO
SERVERS_FOLDER = r"Infraestructura\Fichas Tecnicas Infraestructura"
OUTPUT_FOLDER = r"_yaml_sugerido\infraestructura"

def clean(v):
    if not v:
        return ""
    return v.strip().replace("**","").replace("[","").replace("]","")

def find(pattern, text):
    m = re.search(pattern, text, re.IGNORECASE)
    return clean(m.group(1)) if m else ""

def extract_ports(text):
    ports = []
    rows = re.findall(r"\|\s*(\d+)\s*\|\s*([A-Za-z0-9]+)\s*\|", text)
    for p in rows:
        ports.append({"puerto": p[0], "protocolo": p[1]})
    return ports

def extract_vms(text):
    vms = []
    rows = re.findall(r"\|\s*\*\*(VM-[0-9]+)\*\*\s*\|\s*([^\|]+)\|", text)
    for r in rows:
        vms.append({"nombre": clean(r[0]), "so": clean(r[1])})
    return vms

def extract_apps(text):
    apps = []
    rows = re.findall(r"\|\s*\*\*?([A-Za-z0-9\-\s]+)\*\*?\s*\|\s*([^\|]+)\|", text)
    for r in rows:
        name = clean(r[0])
        if name.lower() not in ["aplicativo", "intranet"]:
            apps.append(name)
    return list(set(apps))

def generate_yaml(name, text):

    data = {
        "tipo": "servidor",
        "nombre": name,
        "modelo": find(r"Modelo:\s*\|\s*([^\|]+)", text),
        "fabricante": find(r"Fabricante:\s*\|\s*([^\|]+)", text),
        "tipo_servidor": find(r"Tipo de servidor:\s*\|\s*([^\|]+)", text),
        "ubicacion": find(r"Ubicación:\s*\|\s*([^\|]+)", text),
        "prioridad": find(r"Priridad\s*\|\s*([^\n]+)", text),
        "sistema_operativo": find(r"Sistema operativo:\s*\|\s*([^\|]+)", text),
        "version_so": find(r"Versión del sistema operativo:\s*\|\s*([^\|]+)", text),
        "virtualizador": find(r"Controlador de virtualización:\s*\|\s*([^\|]+)", text),
        "ip": find(r"Dirección IP pública/privada:\s*\[([^\]]+)\]", text),
        "dns": find(r"Configuración de DNS:\s*\[([^\]]+)\]", text),
        "puertos": extract_ports(text),
        "vms": extract_vms(text),
        "aplicaciones": extract_apps(text),
        "tags": ["activo","servidor"]
    }

    yaml = "---\n"
    for k,v in data.items():
        if isinstance(v, list):
            yaml += f"{k}:\n"
            for item in v:
                yaml += f"  - {item}\n"
        else:
            yaml += f"{k}: {v}\n"
    yaml += "---\n"
    return yaml

def main():

    folder = os.path.join(VAULT_PATH, SERVERS_FOLDER)
    out = os.path.join(VAULT_PATH, OUTPUT_FOLDER)

    os.makedirs(out, exist_ok=True)

    for file in os.listdir(folder):

        if not file.endswith(".md"):
            continue

        path = os.path.join(folder, file)

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        name = file.replace(".md","")

        yaml = generate_yaml(name, text)

        out_file = os.path.join(out, name + ".yml")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(yaml)

        print("Generado:", name)

if __name__ == "__main__":
    main()
