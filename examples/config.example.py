"""
Archivo de configuración de ejemplo para Media Library Organizer.

Copia este archivo y personalízalo según tu configuración:
    cp config.example.py config.py
"""

# Rutas de las bibliotecas
MOVIES_PATH = "/mnt/PROD/MEDIA/Downloads/Movies"
SERIES_PATH = "/mnt/PROD/MEDIA/Downloads/Series"
DUPLICATES_PATH = "/mnt/PROD/MEDIA/Duplicados"

# Extensiones de video soportadas
VIDEO_EXTENSIONS = ['.mkv', '.mp4', '.avi', '.m4v', '.mov']

# Extensiones de metadata soportadas
METADATA_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.nfo', '.srt', '.sub', '.idx']

# Patrones de calidad para detección (ordenados por prioridad)
QUALITY_PATTERNS = [
    '2160p',  # 4K
    '4K',
    '1080p',  # Full HD
    '720p',   # HD
    '480p'    # SD
]

# Códecs de video (ordenados por preferencia)
VIDEO_CODECS = [
    'H.265',
    'HEVC',
    'x265',
    'H.264',
    'x264'
]

# Tipos de HDR (ordenados por preferencia)
HDR_TYPES = [
    'DV',           # Dolby Vision
    'HDR10+',
    'HDR10',
    'HDR'
]

# Códecs de audio (ordenados por preferencia)
AUDIO_CODECS = [
    'Atmos',
    'TrueHD',
    'DTS-HD',
    'DDP7.1',
    'DD7.1',
    'DDP5.1',
    'DD5.1',
    'AAC',
    'AC3'
]

# Palabras clave para idiomas
LANGUAGE_KEYWORDS = {
    'DUAL': ['DUAL'],
    'Latino': ['Latino', 'Spanish'],
    'Castellano': ['Castellano'],
    'English': ['English', 'Ingles']
}

# Estructura de carpetas para películas
# Usa {title} para el título y {year} para el año
MOVIE_FOLDER_FORMAT = "{title} ({year})"

# Nombres de archivos de metadata (para renombrado)
METADATA_NAMES = {
    'poster': ['poster', 'cover'],
    'backdrop': ['backdrop', 'fanart', 'background', 'landscape'],
    'logo': ['logo'],
    'nfo': ['movie', 'info']
}

# Configuración de duplicados
DUPLICATE_CRITERIA = {
    # Orden de prioridad para determinar la mejor versión
    'priority': [
        'resolution',    # Mayor resolución primero
        'hdr',          # HDR sobre SDR
        'dual_audio',   # Audio dual sobre single
        'audio_quality',# Mejor calidad de audio
        'codec',        # Mejor códec
        'size'          # Mayor tamaño (generalmente mejor bitrate)
    ],
    
    # Acción por defecto con duplicados
    'action': 'move',  # 'move', 'delete', 'report'
}

# Configuración de logging
LOGGING = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': 'media_organizer.log'
}

# Opciones de ejecución
OPTIONS = {
    'dry_run': True,           # Modo simulación por defecto
    'preserve_permissions': True,  # Mantener permisos originales
    'generate_report': True,   # Generar reporte JSON
    'verbose': True            # Output detallado
}

# Exclusiones (carpetas/archivos a ignorar)
EXCLUSIONS = {
    'folders': [
        '.@__thumb',
        '@eaDir',
        'Thumbs',
        '.jellyfin-data'
    ],
    'files': [
        '.DS_Store',
        'Thumbs.db',
        'desktop.ini'
    ]
}

# Configuración específica de Jellyfin/Plex
MEDIA_SERVER = {
    'type': 'jellyfin',  # 'jellyfin', 'plex', 'emby'
    'metadata_format': 'nfo',  # Formato de metadata preferido
    'image_format': 'jpg'      # Formato de imágenes preferido
}
