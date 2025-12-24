# Guía de Uso Detallada

## Tabla de Contenidos

1. [Configuración Inicial](#configuración-inicial)
2. [Organizar Biblioteca de Películas](#organizar-biblioteca-de-películas)
3. [Detectar Duplicados](#detectar-duplicados)
4. [Gestionar Duplicados](#gestionar-duplicados)
5. [Organización de Series](#organización-de-series)
6. [Solución de Problemas](#solución-de-problemas)

## Configuración Inicial

### 1. Requisitos del Sistema

- Python 3.7 o superior
- Acceso SSH (para servidores remotos)
- Permisos de lectura/escritura en carpetas de medios

### 2. Configurar Rutas

Edita las rutas en cada script según tu configuración:

```python
# En organize_media_library.py
MOVIES_PATH = "/ruta/a/tus/peliculas"
SERIES_PATH = "/ruta/a/tus/series"

# En move_duplicates.py
DUPLICATES_PATH = "/ruta/a/carpeta/duplicados"
```

## Organizar Biblioteca de Películas

### Paso 1: Modo Simulación

**Siempre ejecuta primero en modo simulación** para ver qué cambios se realizarán:

```bash
python3 scripts/organize_media_library.py
```

Esto mostrará:
- Qué películas se organizarán
- Carpetas que se crearán
- Archivos que se moverán
- Sin realizar cambios reales

### Paso 2: Revisar el Output

Ejemplo de output:

```
🎬 ORGANIZANDO PELÍCULAS
================================================================================

📦 Venom.The.Last.Dance.2024.mkv
   → Venom The Last Dance 2024 (2024)/
   📎 Archivos relacionados: 5
   🔵 Simulación - no se movió

📊 RESUMEN - PELÍCULAS
================================================================================
✅ Organizadas: 209
⏭️  Omitidas: 7
❌ Errores: 0
```

### Paso 3: Ejecutar en Modo Real

Una vez confirmado que todo se ve bien:

```bash
python3 scripts/organize_media_library.py --execute
```

Se te pedirá confirmación:
```
⚠️  MODO EJECUCIÓN REAL - Se moverán archivos

¿Estás seguro de continuar? (escribe 'SI' para confirmar):
```

### Estructura Resultante

Cada película queda organizada así:

```
Movies/
└── Venom The Last Dance 2024 (2024)/
    ├── Venom.The.Last.Dance.2024.mkv    # Video principal
    ├── poster.jpg                        # Poster simplificado
    ├── backdrop.jpg                      # Fondo simplificado
    ├── logo.png                          # Logo simplificado
    └── movie.nfo                         # Metadata simplificada
```

## Detectar Duplicados

### Ejecutar Detección

```bash
python3 scripts/detect_duplicate_movies.py
```

### Interpretar el Reporte

El script analiza y compara:

```
🎬 Película #1: F1 The Movie (2025)
   Copias encontradas: 2

   ⭐ MEJOR Versión 1:
        📄 Archivo: F1.The.Movie.2025.2160p.mkv
        💾 Tamaño: 27.88 GB
        🎥 Calidad: 4K
        ✨ HDR: Sí
        🔊 Audio: Atmos/7.1
        🌐 Dual: Sí

       Versión 2:
        📄 Archivo: F1.The.Movie.2025.1080p.mkv
        💾 Tamaño: 12.33 GB
        🎥 Calidad: 1080p
        ✨ HDR: No
        🔊 Audio: Atmos/7.1
        🌐 Dual: Sí
```

### Criterios de Comparación

El script marca como "MEJOR" la versión con mayor puntuación basándose en:

1. **Resolución** (4K > 1080p > 720p)
2. **HDR/Dolby Vision** (HDR > SDR)
3. **Audio Dual** (Dual > Single)
4. **Calidad de Audio** (Atmos > 7.1 > 5.1 > Stereo)
5. **Tamaño** (mayor tamaño = mejor calidad general)

### Reporte JSON

Se genera automáticamente `duplicate_movies_report.json`:

```json
{
  "scan_date": "2025-12-16T21:00:00",
  "total_movies": 203,
  "duplicate_movies": 6,
  "duplicates": {
    "f1 the movie|2025": {
      "title": "F1 The Movie 2025",
      "year": 2025,
      "copies": [...]
    }
  }
}
```

## Gestionar Duplicados

### Mover Duplicados a Carpeta Separada

```bash
python3 scripts/move_duplicates.py
```

Este script:

1. ✅ Crea `/mnt/PROD/MEDIA/Duplicados` (o tu ruta configurada)
2. ✅ Mueve las versiones de **menor calidad**
3. ✅ Mantiene las versiones de **mejor calidad** en Movies
4. ✅ Preserva permisos y propietarios

### Resultado

```
Movies/
└── F1 The Movie 2025 (2025)/
    └── F1.The.Movie.2025.2160p.mkv    # ⭐ Mejor calidad (4K)

Duplicados/
└── F1 The Movie 2025 (2025)/
    └── F1.The.Movie.2025.1080p.mkv    # Calidad inferior
```

### Revisar Duplicados

Después de mover:

```bash
ls -lh /mnt/PROD/MEDIA/Duplicados/
du -sh /mnt/PROD/MEDIA/Duplicados/
```

### Eliminar Duplicados (Opcional)

Una vez revisados y confirmados, puedes eliminar:

```bash
rm -rf /mnt/PROD/MEDIA/Duplicados/*
```

⚠️ **Advertencia**: Esta acción es permanente.

## Organización de Series

El script verifica automáticamente la estructura de series:

```
📺 ORGANIZANDO SERIES
================================================================================

📺 Breaking Bad
   ✅ Ya tiene 5 temporada(s) organizadas

📺 Game of Thrones
   ✅ Ya tiene 8 temporada(s) organizadas
```

### Estructura Recomendada para Series

```
Series/
└── Breaking Bad/
    ├── Season 1/
    │   ├── Breaking.Bad.S01E01.mkv
    │   ├── Breaking.Bad.S01E02.mkv
    │   └── ...
    ├── Season 2/
    └── ...
```

El script detecta automáticamente:
- Carpetas `Season XX`
- Carpetas `S01`, `S02`, etc.
- Carpetas `Temporada XX`

## Solución de Problemas

### Error: Permission Denied

**Problema**: No tienes permisos para crear/mover archivos.

**Solución**:
```bash
# Ejecutar con sudo (si tienes permisos)
sudo python3 scripts/organize_media_library.py --execute

# O conectar como root
ssh root@servidor
```

### Error: Año no detectado

**Problema**: Algunas películas no tienen año en el nombre.

**Solución**:
1. Las películas sin año se omiten y se reportan
2. Renombra manualmente añadiendo el año: `Pelicula (2024).mkv`
3. Vuelve a ejecutar el script

### Películas ya organizadas

**Problema**: El script dice "Ya existe" para algunas carpetas.

**Solución**: Es normal. El script omite películas ya organizadas para evitar duplicación.

### Verificar resultados

```bash
# Contar películas organizadas
find /ruta/Movies -maxdepth 1 -type d | wc -l

# Verificar archivos sueltos
find /ruta/Movies -maxdepth 1 -type f -name "*.mkv" | wc -l

# Revisar duplicados
ls -lh /ruta/Duplicados/
```

## Ejecución Remota

### Via SSH

```bash
# Copiar script al servidor
scp scripts/organize_media_library.py user@servidor:/tmp/

# Ejecutar remotamente
ssh user@servidor "python3 /tmp/organize_media_library.py"
```

### Con Root

```bash
# Conectar como root
ssh root@servidor

# Copiar script
cat > /root/organize.py << 'EOF'
[contenido del script]
EOF

# Ejecutar
python3 /root/organize.py --execute
```

## Tips y Mejores Prácticas

### 1. Backup antes de ejecutar

```bash
# Crear snapshot (si usas ZFS/BTRFS)
zfs snapshot pool/media@before-organize

# O hacer backup de la lista de archivos
find /ruta/Movies > backup-file-list.txt
```

### 2. Ejecutar en horario de baja demanda

Las operaciones de I/O pueden ser intensivas. Ejecuta cuando el servidor esté menos ocupado.

### 3. Revisar logs

Guarda el output para referencia:

```bash
python3 scripts/organize_media_library.py --execute | tee organization-log.txt
```

### 4. Actualizar Jellyfin/Plex

Después de organizar, actualiza la biblioteca:

**Jellyfin**: Dashboard → Libraries → Scan All Libraries
**Plex**: Settings → Manage → Libraries → Scan Library Files

## Preguntas Frecuentes

**P: ¿Puedo revertir los cambios?**
R: Sí, si guardaste el reporte JSON. Puedes mover manualmente o escribir un script de reversión.

**P: ¿Afecta a los metadatos de Jellyfin?**
R: Jellyfin re-escaneará y actualizará automáticamente.

**P: ¿Puedo personalizar la estructura de carpetas?**
R: Sí, edita la función `create_movie_folder_name()` en el script.

**P: ¿Qué pasa con subtítulos?**
R: Se mueven junto con la película si tienen el mismo nombre base.

---

**¿Necesitas ayuda adicional?** [Abre un issue en GitHub](https://github.com/tu-usuario/media-library-organizer/issues)
