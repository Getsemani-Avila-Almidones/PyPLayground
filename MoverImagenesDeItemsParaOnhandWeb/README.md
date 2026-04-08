# Organizador de Imágenes de Items para OnHand Web

Script automatizado para organizar carpetas de items con imágenes, creando una estructura limpia y ordenada.

## 🎯 Objetivo

Transformar una estructura desordenada de carpetas SEMANA y subcarpetas en una estructura limpia:

**Antes:**
```
items/
├── SEMANA-01/
│   └── 120-005-003/
│       ├── imagen1.jpg
│       └── imagen2.jpg
├── SEMANA-02/
│   └── N-150-002-001/
│       └── foto.png
└── ...
```

**Después:**
```
items/
├── 120-005-003/
│   └── 120-005-003.jpg
├── N-150-002-001/
│   └── N-150-002-001.png
└── ...
```

## 📁 Estructura del Proyecto

```
MoverImagenesDeItemsParaOnhandWeb/
├── config.py                    # Configuración centralizada
├── main.py                      # Orquestador principal
├── modules/
│   ├── __init__.py
│   ├── scanner.py              # Escaneo de carpetas
│   ├── organizer.py            # Organización y movimiento
│   └── image_processor.py      # Procesamiento de imágenes
└── utils/
    ├── __init__.py
    └── helpers.py              # Funciones auxiliares
```

## ⚙️ Configuración

Edita `config.py` antes de ejecutar:

```python
# Ruta donde se encuentran los items
ROOT_PATH = Path(r"C:\ruta\a\tus\items")

# Modo de prueba (no realiza cambios)
DRY_RUN = True  # Cambiar a False para ejecutar

# Extensiones de imagen válidas
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ...}
```

## 🚀 Uso

**IMPORTANTE**: Antes de ejecutar, edita `config.py` y ajusta:
1. `ROOT_PATH`: La ruta donde están tus carpetas de items
2. `DRY_RUN`: Modo de ejecución

### Modo de Prueba (Recomendado primero)
```bash
# 1. Edita config.py y establece:
#    ROOT_PATH = Path(r"C:\ruta\a\tus\items")
#    DRY_RUN = True

# 2. Ejecuta el script
cd MoverImagenesDeItemsParaOnhandWeb
python main.py
```

### Modo Producción (Después de verificar con DRY-RUN)
```bash
# 1. Edita config.py y establece:
#    DRY_RUN = False

# 2. Ejecuta el script
python main.py
```

## 🔄 Proceso

El script ejecuta 3 pasos principales:

1. **Escaneo**: Identifica todas las carpetas de items con imágenes
2. **Organización**: Mueve las carpetas al directorio raíz (omitiendo SEMANA)
3. **Procesamiento**: Renombra imágenes y elimina duplicados

## ✨ Características

- ✅ Detecta automáticamente carpetas de items (patrón: `XXX-XXX-XXX`)
- ✅ Omite carpetas SEMANA en la estructura final
- ✅ Renombra imágenes al formato `<NumeroDeItem>.<extension>`
- ✅ Elimina duplicados basándose en hash SHA256
- ✅ Modo DRY-RUN para probar sin cambios reales
- ✅ Manejo de conflictos de nombres (agrega sufijos numéricos)
- ✅ Estadísticas detalladas del proceso

## 📊 Salida Ejemplo

```
============================================================
   ORGANIZADOR DE IMAGENES DE ITEMS PARA ONHAND WEB
============================================================
Directorio raiz: C:\Users\...\items
Modo: DRY-RUN (sin cambios reales)
============================================================

============================================================
PASO 0: ESCANEANDO CARPETAS SEMANA (informativo)
============================================================
[*] Carpetas SEMANA encontradas: 15
    Con archivos: 12
    Vacias: 3

============================================================
ESCANEANDO CARPETAS DE ITEMS
============================================================
[*] Items encontrados: 245
    Con imagenes: 198
    Sin imagenes: 47

============================================================
PASO 1: ORGANIZANDO CARPETAS DE ITEMS
============================================================
[OK] Movida: 120-005-003 -> C:\...\items\120-005-003
...

============================================================
PASO 2: PROCESANDO IMAGENES
============================================================
[*] Procesando: 120-005-003
  [OK] Renombrada: imagen1.jpg -> 120-005-003.jpg
  [OK] Eliminado duplicado: imagen2.jpg
...

============================================================
   RESUMEN FINAL
============================================================

[ESCANEO]
   Items encontrados: 245
   Items con imagenes: 198
   Items sin imagenes: 47

[ORGANIZACION]
   Carpetas movidas: 198
   Carpetas omitidas: 0

[PROCESAMIENTO DE IMAGENES]
   Carpetas procesadas: 198
   Imagenes renombradas: 145
   Duplicados eliminados: 87
   Advertencias: 3

============================================================
[OK] PROCESO COMPLETADO EXITOSAMENTE
============================================================
```

## ⚠️ Notas Importantes

- **Siempre ejecuta primero en modo DRY-RUN** para verificar los cambios
- Realiza un **backup** de tus datos antes de ejecutar en producción
- Las carpetas SEMANA vacías no se eliminan automáticamente
- Las imágenes con diferente hash no se eliminan (se genera advertencia)

## 🐛 Troubleshooting

### Error: "No existe el directorio raíz"
- Verifica que `ROOT_PATH` en `config.py` sea correcto
- Asegúrate de que el directorio existe y tienes permisos

### Advertencia: "Imagen diferente encontrada"
- El script encontró múltiples imágenes con diferente contenido
- Revisa manualmente estas carpetas para decidir cuál conservar

## 📝 Scripts Originales

Los scripts originales se mantienen en el directorio para referencia:
- `BuscarArchivosCarpetasSEMANA.py` (ahora integrado en scanner.py)
- `RevisarDuplicadosUnificar.py` (ahora integrado en image_processor.py)
