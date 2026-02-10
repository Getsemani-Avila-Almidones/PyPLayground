##from modules.apps.apps import execute as run_apps
##from modules.servers.servers import execute as run_servers
from modules.general_analysis import analyze_vault
from config import VAULT_PATH, OUTPUT_DATA

def banner():
    print("\n====================================")
    print("  OBSIDIAN CMDB ANALYZER")
    print("  Auditor de Conocimiento TI")
    print("====================================\n")

def main():

    banner()
    # Ejecutar Reporte General
    analyze_vault()

    # Ejecutar Apps
    #run_apps()

    # Ejecutar Servidores
    #run_servers()

    print("\n====================================")
    print("ANALISIS COMPLETADO")
    print("Revisa la carpeta _yaml_sugerido")
    print("====================================\n")

if __name__ == "__main__":
    main()
