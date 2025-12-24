#!/bin/bash
# Quick Setup - Configuración rápida para Media Library Organizer

echo "=== Media Library Organizer - Configuración Rápida ==="
echo ""

# Verificar si estamos ejecutando desde el directorio correcto
if [ ! -f "config.yaml" ]; then
    echo "Error: config.yaml no encontrado"
    echo "Ejecuta este script desde el directorio media-library-organizer/"
    exit 1
fi

# Función para pedir input con valor por defecto
ask_with_default() {
    local prompt="$1"
    local default="$2"
    local varname="$3"
    
    read -p "$prompt [$default]: " value
    value="${value:-$default}"
    eval "$varname='$value'"
}

echo "Vamos a configurar tus directorios de medios"
echo ""

# Movies
echo "=== PELÍCULAS ==="
ask_with_default "Carpeta de descargas de películas" "/mnt/downloads/movies" MOVIES_SOURCE
ask_with_default "Biblioteca de películas (Jellyfin/Plex)" "/mnt/media/Movies" MOVIES_DEST
ask_with_default "¿Habilitar organización de películas? (true/false)" "true" MOVIES_ENABLED

echo ""

# Series
echo "=== SERIES ==="
ask_with_default "Carpeta de descargas de series" "/mnt/downloads/series" SERIES_SOURCE
ask_with_default "Biblioteca de series" "/mnt/media/Series" SERIES_DEST
ask_with_default "¿Habilitar organización de series? (true/false)" "true" SERIES_ENABLED

echo ""

# Anime
echo "=== ANIME (Opcional) ==="
ask_with_default "Carpeta de descargas de anime" "/mnt/downloads/anime" ANIME_SOURCE
ask_with_default "Biblioteca de anime" "/mnt/media/Anime" ANIME_DEST
ask_with_default "¿Habilitar organización de anime? (true/false)" "false" ANIME_ENABLED

echo ""

# Settings
echo "=== CONFIGURACIÓN ==="
ask_with_default "Modo dry-run (simulación sin cambios reales)? (true/false)" "true" DRY_RUN
ask_with_default "¿Mover o copiar archivos? (move/copy)" "move" MOVE_OR_COPY
ask_with_default "Tamaño mínimo de archivo en MB" "100" MIN_SIZE

echo ""
echo "Generando config.yaml..."

cat > config.yaml << EOF
# Media Library Organizer - Configuración
# Generado el: $(date)

directories:
  movies:
    source: "$MOVIES_SOURCE"
    destination: "$MOVIES_DEST"
    enabled: $MOVIES_ENABLED
    auto_organize: true
    
  series:
    source: "$SERIES_SOURCE"
    destination: "$SERIES_DEST"
    enabled: $SERIES_ENABLED
    auto_organize: true
    
  anime:
    source: "$ANIME_SOURCE"
    destination: "$ANIME_DEST"
    enabled: $ANIME_ENABLED
    auto_organize: false

settings:
  dry_run: $DRY_RUN
  preserve_permissions: true
  create_nfo_files: false
  move_or_copy: "$MOVE_OR_COPY"
  min_file_size_mb: $MIN_SIZE
  
  duplicates:
    detect: true
    auto_delete_lower_quality: false
    move_to_folder: null
    
  video_extensions:
    - .mkv
    - .mp4
    - .avi
    - .m4v
    - .mov
    - .wmv
    
  metadata_extensions:
    - .jpg
    - .jpeg
    - .png
    - .nfo
    - .srt
    - .sub
    - .idx
    - .ass

schedule:
  enabled: false
  interval: "hourly"
  custom_cron: "0 */2 * * *"

notifications:
  enabled: false
  discord_webhook: null
  telegram_bot_token: null
  telegram_chat_id: null

logging:
  enabled: true
  log_file: "/var/log/media-organizer/organizer.log"
  log_level: "INFO"
  max_log_size_mb: 10
  backup_count: 5
EOF

echo ""
echo "✓ config.yaml generado exitosamente"
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Revisa la configuración:"
echo "   nano config.yaml"
echo ""
echo "2. Prueba en modo dry-run:"
echo "   python3 scripts/auto_organizer.py"
echo ""
echo "3. Si todo está bien, desactiva dry_run:"
echo "   sed -i 's/dry_run: true/dry_run: false/' config.yaml"
echo ""
echo "4. Instala el servicio (opcional):"
echo "   sudo bash install.sh"
echo ""
