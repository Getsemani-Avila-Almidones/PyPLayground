def detect_type(name, folder, content):

    n = name.lower()

    # SERVIDORES
    if "dcamxv" in n or "server" in n or "servidor" in n:
        return "servidor"

    # BASES DE DATOS
    if "base de datos" in n or "oracle" in n or "db" in n:
        return "base_datos"

    # DOCUMENTOS / INDICES
    if "index" in n or "clasificación" in n or "catalogo" in n:
        return "documentacion"

    # POLÍTICAS
    if "certificado" in n or "politica" in n:
        return "politica"

    # PROCESOS
    if "proceso" in folder.lower():
        return "proceso"

    # APLICACIONES (default)
    return "aplicacion"

