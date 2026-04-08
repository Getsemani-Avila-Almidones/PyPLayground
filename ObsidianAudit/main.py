import sys
from modules.general_analysis import analyze_vault
from modules.apps.apps_smart import execute as run_apps
from modules.servers.servers_smart import execute as run_servers
from modules.dashboard import execute_dashboard
from modules.apply_yaml import execute_apply


def banner():
    print("\n====================================")
    print("  OBSIDIAN CMDB ANALYZER")
    print("  Auditor de Conocimiento TI")
    print("====================================\n")

def main():

    banner()
    # Ejecutar Reporte General
    # analyze_vault()

    # Ejecutar Apps
    # run_apps()

    # Ejecutar Servidores
    # run_servers()

    # Aplicar YAML solo si se solicita
    # execute_apply()
    # if "--apply" in sys.argv:
    #     execute_apply()

    # Dashboard final
    # execute_dashboard()

    print("\n====================================")
    print("ANALISIS COMPLETADO")
    print("Revisa la carpeta _yaml_sugerido")
    print("====================================\n")

if __name__ == "__main__":
    main()
