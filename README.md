# Media Library Organizer

Sistema automatizado para organizar bibliotecas multimedia (películas, series, anime, documentales) compatible con Jellyfin, Plex y Emby.

## 🎯 Características

- ✅ **Organización automática de múltiples categorías** (películas, series, anime, documentales)
- ✅ **Ejecución programada** vía cron o systemd timer
- ✅ **Configuración multi-directorio** con YAML
- ✅ **Detección de duplicados** con análisis de calidad (4K, HDR, audio)
- ✅ **Gestión de metadata** (subtítulos, NFO, posters)
- ✅ **Logging detallado** con rotación automática
- ✅ **Compatible con Jellyfin/Plex/Emby**
- ✅ **Modo simulación (dry-run)** para probar sin modificar archivos
- ✅ **Notificaciones opcionales** (Discord, Telegram, Email)

## 📁 Estructura del Proyecto

```
media-library-organizer/
├── scripts/
│   ├── auto_organizer.py          # ⭐ Organizador automático mejorado
│   ├── organize_media_library.py  # Organizador manual original
│   ├── detect_duplicate_movies.py # Detector de duplicados
│   └── move_duplicates.py         # Mover duplicados a carpeta separada
├── config.yaml                     # ⭐ Configuración principal
├── install.sh                      # ⭐ Script de instalación
├── docs/
│   └── USAGE.md                   # Guía de uso detallada
├── examples/
│   └── config.example.py          # Ejemplo de configuración
├── README.md                      # Este archivo
└── LICENSE                        # Licencia MIT
```

## 🚀 Instalación y Configuración

### Opción 1: Instalación Automática (Recomendada)

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/media-library-organizer.git
cd media-library-organizer

# Ejecutar instalador
sudo bash install.sh
```

El instalador:
- ✅ Instala dependencias (Python 3, PyYAML)
- ✅ Copia archivos a `/opt/media-organizer`
- ✅ Crea config en `/etc/media-organizer/config.yaml`
- ✅ Configura logs en `/var/log/media-organizer`
- ✅ Opcionalmente instala systemd timer o cron job

### Opción 2: Instalación Manual

```bash
# Instalar dependencias
sudo apt install python3 python3-pip python3-yaml  # Ubuntu/Debian
# o
sudo yum install python3 python3-pip python3-pyyaml  # CentOS/RHEL

# Clonar repositorio
git clone https://github.com/tu-usuario/media-library-organizer.git
cd media-library-organizer

# Instalar dependencias de Python
pip3 install pyyaml
```

### Configuración

Edita el archivo `config.yaml`:

```bash
sudo nano /etc/media-organizer/config.yaml
# o si no usaste install.sh:
nano config.yaml
```

**Ejemplo de configuración:**

```yaml
directories:
  movies:
    source: "/mnt/downloads/movies"
    destination: "/mnt/media/Movies"
    enabled: true
    auto_organize: true
    
  series:
    source: "/mnt/downloads/series"
    destination: "/mnt/media/Series"
    enabled: true
    auto_organize: true

settings:
  dry_run: true  # Cambia a false cuando estés listo
  move_or_copy: "move"
  min_file_size_mb: 100
```
python3 scripts/organize_media_library.py
```

**Modo ejecución real:**
```bash
python3 scripts/organize_media_library.py --execute
```

#### 2. Detectar Duplicados

```bash
python3 scripts/detect_duplicate_movies.py
```

Este script genera un reporte JSON con:
- Películas duplicadas detectadas
- Comparación de calidad (resolución, HDR, audio)
- Recomendación de qué versión mantener
- Espacio desperdiciado

#### 3. Mover Duplicados

```bash
python3 scripts/move_duplicates.py
```

Mueve las versiones de menor calidad a `/mnt/PROD/MEDIA/Duplicados`

## 📊 Ejemplo de Resultado

### Antes
```
Movies/
├── Venom.The.Last.Dance.2024.2160p.mkv
├── Venom.The.Last.Dance.2024-poster.jpg
├── Venom.The.Last.Dance.2024-backdrop.jpg
├── The.Wild.Robot.2024.mkv
└── ...
```

### Después
```
Movies/
├── Venom The Last Dance 2024 (2024)/
│   ├── Venom.The.Last.Dance.2024.mkv
│   ├── poster.jpg
│   ├── backdrop.jpg
│   ├── logo.png
│   └── movie.nfo
├── The Wild Robot 2024 (2024)/
│   ├── The.Wild.Robot.2024.mkv
│   └── ...
```

## 🔍 Detección de Duplicados

El sistema detecta duplicados basándose en:

1. **Título normalizado** (ignora calidad, códecs, idiomas)
2. **Año de lanzamiento**
3. **Comparación de calidad:**
   - Resolución (4K > 1080p > 720p)
   - HDR/Dolby Vision
   - Audio dual (Latino + Inglés)
   - Calidad de audio (Atmos > 5.1 > Stereo)

### Ejemplo de Detección

```
🎬 Película: F1 The Movie (2025)
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
```

## ⚙️ Configuración

Edita las rutas en los scripts según tu configuración:

```python
MOVIES_PATH = "/mnt/PROD/MEDIA/Downloads/Movies"
SERIES_PATH = "/mnt/PROD/MEDIA/Downloads/Series"
DUPLICATES_PATH = "/mnt/PROD/MEDIA/Duplicados"
```

## 🛡️ Seguridad

- ✅ **Modo simulación por defecto** - no modifica archivos sin confirmación
- ✅ **Preservación de permisos** - mantiene propietario y permisos originales
- ✅ **Reportes JSON** - registro completo de todas las operaciones
- ✅ **Sin eliminación automática** - duplicados se mueven, no se borran

## 📈 Resultados de Ejemplo

Caso real de uso:

- **216 películas** procesadas
- **209 películas** organizadas exitosamente
- **6 duplicados** detectados
- **65 GB** de espacio en duplicados
- **0 errores** de permisos
- **251 carpetas** totales organizadas

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

- **Tu Nombre** - [GitHub](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- Compatible con [Jellyfin](https://jellyfin.org/), [Plex](https://www.plex.tv/), y [Emby](https://emby.media/)
- Inspirado en las mejores prácticas de organización de medios

## 📞 Soporte

Si encuentras algún problema o tienes sugerencias:

- 🐛 [Reportar un bug](https://github.com/tu-usuario/media-library-organizer/issues)
- 💡 [Solicitar una característica](https://github.com/tu-usuario/media-library-organizer/issues)
- 📧 [Contacto directo](mailto:tu-email@example.com)

---

**¿Te resultó útil este proyecto? ⭐ Dale una estrella en GitHub!**

## 📖 Uso

### Ejecución Manual

```bash
# Modo dry-run (simulación - no modifica nada)
sudo python3 /opt/media-organizer/auto_organizer.py

# o si no instalaste:
python3 scripts/auto_organizer.py
```

### Ejecución Automática

#### Con Systemd Timer (Recomendado)

```bash
# Iniciar el timer
sudo systemctl start media-organizer.timer

# Ver estado
sudo systemctl status media-organizer.timer

# Ver próximas ejecuciones
systemctl list-timers media-organizer.timer

# Deshabilitar
sudo systemctl stop media-organizer.timer
sudo systemctl disable media-organizer.timer
```

#### Con Cron

```bash
# Editar crontab
sudo crontab -e

# Agregar línea (ejemplo: cada 2 horas)
0 */2 * * * /usr/bin/python3 /opt/media-organizer/auto_organizer.py >> /var/log/media-organizer/cron.log 2>&1
```

### Ver Logs

```bash
# Ver logs en tiempo real
tail -f /var/log/media-organizer/organizer.log

# Ver últimas 50 líneas
tail -n 50 /var/log/media-organizer/organizer.log

# Buscar errores
grep ERROR /var/log/media-organizer/organizer.log
```

## 🎬 Ejemplos de Organización

### Antes (Carpeta de Descargas)
```
/mnt/downloads/movies/
├── The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv
├── Inception.2010.2160p.WEB-DL.DDP5.1.x265-RELEASE.mkv
├── Interstellar.2014.IMAX.1080p.BluRay.mkv
└── The.Dark.Knight.2008.4K.UHD.HDR.mkv
```

### Después (Biblioteca Organizada)
```
/mnt/media/Movies/
├── The Matrix (1999)/
│   └── The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv
├── Inception (2010)/
│   ├── Inception.2010.2160p.WEB-DL.DDP5.1.x265-RELEASE.mkv
│   └── Inception.2010.srt
├── Interstellar (2014)/
│   └── Interstellar.2014.IMAX.1080p.BluRay.mkv
└── The Dark Knight (2008)/
    └── The.Dark.Knight.2008.4K.UHD.HDR.mkv
```

## ⚙️ Configuración Avanzada

### Programación Personalizada

Edita el timer de systemd:

```bash
sudo systemctl edit media-organizer.timer
```

Cambia la frecuencia:

```ini
[Timer]
OnCalendar=*-*-* 03:00:00  # Diario a las 3:00 AM
# o
OnCalendar=*:0/30          # Cada 30 minutos
# o  
OnCalendar=Mon *-*-* 00:00:00  # Cada lunes a medianoche
```

### Notificaciones

Edita `config.yaml`:

```yaml
notifications:
  enabled: true
  discord_webhook: "https://discord.com/api/webhooks/..."
  # o
  telegram_bot_token: "tu_token"
  telegram_chat_id: "tu_chat_id"
```

### Múltiples Categorías

```yaml
directories:
  movies_4k:
    source: "/downloads/movies-4k"
    destination: "/media/Movies-4K"
    enabled: true
    
  anime:
    source: "/downloads/anime"
    destination: "/media/Anime"
    enabled: true
    
  documentaries:
    source: "/downloads/docs"
    destination: "/media/Documentaries"
    enabled: true
```

## 🔧 Solución de Problemas

### El script no organiza nada

1. **Verifica que dry_run esté en `false`:**
   ```bash
   grep dry_run /etc/media-organizer/config.yaml
   ```

2. **Revisa los logs:**
   ```bash
   tail -f /var/log/media-organizer/organizer.log
   ```

3. **Verifica permisos:**
   ```bash
   ls -la /mnt/downloads/movies
   ls -la /mnt/media/Movies
   ```

### Errores de permisos

```bash
# Ejecutar como root o con sudo
sudo python3 /opt/media-organizer/auto_organizer.py

# O dar permisos al usuario
sudo chown -R tu_usuario:tu_usuario /mnt/media
```

### Los archivos no se mueven

- Verifica que las rutas en `config.yaml` sean correctas
- Asegúrate de que `auto_organize: true` esté activado
- Revisa que los archivos cumplan el tamaño mínimo (min_file_size_mb)

## 📝 Comandos Útiles

```bash
# Ver estado completo
sudo python3 /opt/media-organizer/auto_organizer.py

# Ver solo errores
sudo python3 /opt/media-organizer/auto_organizer.py 2>&1 | grep ERROR

# Ejecutar en segundo plano
nohup sudo python3 /opt/media-organizer/auto_organizer.py > /tmp/organizer.log 2>&1 &

# Ver procesos en ejecución
ps aux | grep auto_organizer

# Matar proceso si se colgó
pkill -f auto_organizer.py
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- Inspirado en las mejores prácticas de Jellyfin, Plex y Emby
- Gracias a la comunidad de /r/DataHoarder y /r/selfhosted

---

**Autor**: @miures  
**Repositorio**: https://github.com/miures/media-library-organizer  
**Versión**: 2.0 (Automatizada)
