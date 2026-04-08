import os

# Ruta raíz del vault
VAULT_PATH = r"C:\Users\21596\Documents\Obsidian\AlmexVault"

# Carpeta de datos generados
OUTPUT_DATA = os.path.join(VAULT_PATH, "_obsidian_data")

# YAML sugeridos
OUTPUT_APPS = os.path.join(VAULT_PATH, "_yaml_sugerido", "apps")
OUTPUT_SERVERS = os.path.join(VAULT_PATH, "_yaml_sugerido", "infraestructura")


# Carpetas donde la migración queda ACTIVADA actualmente.
ACTIVE_MODULE_FOLDERS = {
    os.path.normpath("Application/Fichas Tecnicas Aplicaciones"),
    os.path.normpath("Infraestructura/Fichas Tecnicas Infraestructura"),
}

# Carpetas reservadas para futuros módulos. Se dejan explícitas para
# facilitar su activación posterior sin tocar la lógica principal.
FUTURE_MODULE_FOLDERS = {
    os.path.normpath("Listas de distribución OTBI"),
    os.path.normpath("Incidentes/INFORMES"),
    os.path.normpath("OIC_APEX"),
    os.path.normpath("Politicas"),
    os.path.normpath("Procesos"),
    os.path.normpath("Procesos/Ficha Tecnicas Procesos"),
}
