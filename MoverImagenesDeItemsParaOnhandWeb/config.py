from pathlib import Path
import re

# =========================
# CONFIGURACIÓN PRINCIPAL
# =========================

# Ruta raíz donde se encuentran las carpetas de items
ROOT_PATH = Path(r"C:\Users\21596\Documents\Dev\rptOnHandWeb\assets\items")

# Modo de prueba: no realiza cambios reales, solo muestra lo que haría
# IMPORTANTE: Cambiar a False solo cuando estés seguro de ejecutar
DRY_RUN = False

# Extensiones de imagen válidas
IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".bmp", ".tif", ".tiff", ".jfif", ".avif", ".svg"
}

# Patrón para identificar carpetas de items
# Ejemplos: 120-005-003, N-120-005-003, A-120-005-003
ITEM_PATTERN = re.compile(r"^(?:[A-Za-z]-)?[A-Za-z0-9]+-[A-Za-z0-9]+-[A-Za-z0-9]+$")

# Tamaño del chunk para calcular hash de archivos (1 MB)
HASH_CHUNK_SIZE = 1024 * 1024

# Cantidad máxima de carpetas a mostrar en detalle durante el procesamiento
# (para evitar salida excesiva con miles de items)
MAX_VERBOSE_ITEMS = 50
