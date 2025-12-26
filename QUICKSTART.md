# 🎬 Media Library Organizer v2.0 - Guía de Inicio Rápido

## ✨ Nuevas Características

Tu proyecto de organización de películas ha sido actualizado con:

### 1. **Sistema Automatizado Completo**
- ✅ Ejecución programada (cron o systemd timer)
- ✅ Configuración multi-directorio (películas, series, anime, docs)
- ✅ Logging detallado con rotación automática
- ✅ Modo dry-run para pruebas seguras

### 2. **Archivos Nuevos**

```
media-library-organizer/
├── config.yaml               # ⭐ Configuración principal YAML
├── install.sh               # ⭐ Instalador automatizado
├── quick-setup.sh           # ⭐ Setup interactivo rápido
├── scripts/
│   └── auto_organizer.py    # ⭐ Script automatizado mejorado
└── examples/
    └── config-truenas.yaml  # ⭐ Ejemplo para tu servidor
```

## 🚀 Cómo Usar

### Opción 1: Quick Setup (Más Fácil)

```bash
cd /home/asanchez/media-library-organizer

# Configuración interactiva
./quick-setup.sh

# Prueba en modo simulación
python3 scripts/auto_organizer.py

# Si está bien, desactiva dry-run
sed -i 's/dry_run: true/dry_run: false/' config.yaml

# Ejecuta de verdad
python3 scripts/auto_organizer.py
```

### Opción 2: Instalación Completa en Servidor

```bash
# En tu máquina local
cd /home/asanchez/media-library-organizer

# Copiar a servidor (ajusta la IP y rutas)
scp -r . root@192.168.1.12:/tmp/media-organizer/

# SSH al servidor
ssh root@192.168.1.12

# Instalar
cd /tmp/media-organizer
bash install.sh

# Editar configuración
nano /etc/media-organizer/config.yaml

# Probar
python3 /opt/media-organizer/auto_organizer.py

# Ver logs
tail -f /var/log/media-organizer/organizer.log
```

## 📋 Pasos Recomendados

### 1. Configurar Rutas

Edita `config.yaml` con tus rutas reales:

```yaml
directories:
  movies:
    source: "/ruta/a/descargas/movies"
    destination: "/ruta/a/jellyfin/Movies"
    enabled: true
    auto_organize: true
```

### 2. Probar en Dry-Run

```bash
# Primera prueba (no modifica nada)
python3 scripts/auto_organizer.py

# Revisa los logs
cat /var/log/media-organizer/organizer.log
```

### 3. Ejecutar de Verdad

```bash
# Cambiar en config.yaml:
dry_run: false

# Ejecutar
python3 scripts/auto_organizer.py
```

### 4. Automatizar

#### Con Systemd (Recomendado para servidores Linux)

```bash
# Durante install.sh, elige "Yes" para systemd
sudo bash install.sh

# Iniciar timer
sudo systemctl start media-organizer.timer

# Ver estado
systemctl status media-organizer.timer
```

#### Con Cron (Alternativa)

```bash
# Durante install.sh, elige "Yes" para cron
# O manualmente:
sudo crontab -e

# Agregar (cada 2 horas):
0 */2 * * * /usr/bin/python3 /opt/media-organizer/auto_organizer.py >> /var/log/media-organizer/cron.log 2>&1
```

## 🎯 Ejemplos de Uso

### Para tu TrueNAS (192.168.1.12)

Usa el archivo `examples/config-truenas.yaml` como base:

```bash
# Copiar ejemplo
cp examples/config-truenas.yaml config.yaml

# Editar con tus rutas reales
nano config.yaml

# Ajustar rutas de qBittorrent y Jellyfin
```

**Ejemplo de rutas TrueNAS:**
- Descargas qBittorrent Movies: `/mnt/tank/downloads/qbittorrent-movies/completed`
- Descargas qBittorrent Anime: `/mnt/tank/downloads/qbittorrent-anime/completed`
- Biblioteca Jellyfin Movies: `/mnt/tank/media/Movies`
- Biblioteca Jellyfin Anime: `/mnt/tank/media/Anime`

### Comandos Útiles

```bash
# Ver logs en tiempo real
tail -f /var/log/media-organizer/organizer.log

# Ejecutar manualmente
python3 /opt/media-organizer/auto_organizer.py

# Ver próximas ejecuciones del timer
systemctl list-timers media-organizer.timer

# Detener automatización
sudo systemctl stop media-organizer.timer

# Ver estadísticas
grep "Resumen de ejecución" /var/log/media-organizer/organizer.log | tail -5
```

## 🔧 Configuración Avanzada

### Programar Horarios Específicos

Edita el timer de systemd:

```bash
sudo systemctl edit media-organizer.timer
```

```ini
[Timer]
OnCalendar=*-*-* 03:00:00  # Diario a las 3 AM
```

Opciones de `OnCalendar`:
- `hourly` = Cada hora
- `*:0/30` = Cada 30 minutos
- `*-*-* 03:00:00` = Diario a las 3 AM
- `Mon *-*-* 00:00:00` = Cada lunes a medianoche

### Notificaciones (Futuro)

En `config.yaml`:

```yaml
notifications:
  enabled: true
  discord_webhook: "https://discord.com/api/webhooks/..."
```

## 📊 Logs y Monitoreo

```bash
# Ver últimas ejecuciones
grep "Iniciando Media Library Organizer" /var/log/media-organizer/organizer.log

# Ver errores
grep ERROR /var/log/media-organizer/organizer.log

# Ver cuántos archivos se procesaron
grep "Procesados:" /var/log/media-organizer/organizer.log | tail -10
```

## 🐛 Solución de Problemas

### "No se encuentran archivos"
- Verifica las rutas en `config.yaml`
- Asegúrate de que `enabled: true`
- Revisa permisos de lectura en las carpetas

### "Permission denied"
- Ejecuta con `sudo` o como root
- Verifica permisos de las carpetas destino

### "Archivos no se mueven"
- Verifica que `dry_run: false`
- Revisa que `auto_organize: true`
- Confirma que los archivos cumplan el tamaño mínimo

## 📞 Soporte

- **Logs**: `/var/log/media-organizer/organizer.log`
- **Config**: `/etc/media-organizer/config.yaml`
- **Scripts**: `/opt/media-organizer/`

---

**¡Listo para organizar tu biblioteca automáticamente!** 🎉
