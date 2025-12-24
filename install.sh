#!/bin/bash
# Script de instalación del Media Library Organizer

set -e

echo "=== Media Library Organizer - Instalación ==="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directorio de instalación
INSTALL_DIR="/opt/media-organizer"
CONFIG_DIR="/etc/media-organizer"
LOG_DIR="/var/log/media-organizer"

# Verificar si es root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Este script debe ejecutarse como root${NC}"
  echo "Usa: sudo bash install.sh"
  exit 1
fi

echo -e "${GREEN}1. Instalando dependencias de Python...${NC}"
if command -v apt-get &> /dev/null; then
    apt-get update
    apt-get install -y python3 python3-pip python3-yaml
elif command -v yum &> /dev/null; then
    yum install -y python3 python3-pip python3-pyyaml
elif command -v dnf &> /dev/null; then
    dnf install -y python3 python3-pip python3-pyyaml
else
    echo -e "${YELLOW}Gestor de paquetes no detectado. Instala Python 3 y PyYAML manualmente.${NC}"
fi

pip3 install pyyaml --upgrade 2>/dev/null || true

echo ""
echo -e "${GREEN}2. Creando directorios...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$LOG_DIR"

echo ""
echo -e "${GREEN}3. Copiando archivos...${NC}"
cp -r scripts/* "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/auto_organizer.py"

# Copiar config si no existe
if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
    cp config.yaml "$CONFIG_DIR/config.yaml"
    echo -e "${YELLOW}Config copiado a: $CONFIG_DIR/config.yaml${NC}"
    echo -e "${YELLOW}¡IMPORTANTE! Edita este archivo con tus rutas${NC}"
else
    echo -e "${YELLOW}Config ya existe, no se sobrescribe${NC}"
fi

echo ""
echo -e "${GREEN}4. Configurando permisos...${NC}"
chmod 755 "$INSTALL_DIR"
chmod 644 "$CONFIG_DIR/config.yaml"
chmod 755 "$LOG_DIR"

echo ""
echo -e "${GREEN}5. ¿Deseas instalar el servicio systemd? (recomendado) [y/N]${NC}"
read -r install_systemd

if [[ "$install_systemd" =~ ^[Yy]$ ]]; then
    cat > /etc/systemd/system/media-organizer.service <<EOF
[Unit]
Description=Media Library Organizer
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 $INSTALL_DIR/auto_organizer.py
WorkingDirectory=$INSTALL_DIR
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    cat > /etc/systemd/system/media-organizer.timer <<EOF
[Unit]
Description=Media Library Organizer Timer
Requires=media-organizer.service

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
EOF

    systemctl daemon-reload
    systemctl enable media-organizer.timer
    
    echo -e "${GREEN}✓ Servicio systemd instalado${NC}"
    echo -e "  Inicia con: ${YELLOW}systemctl start media-organizer.timer${NC}"
    echo -e "  Ver estado: ${YELLOW}systemctl status media-organizer.timer${NC}"
fi

echo ""
echo -e "${GREEN}6. ¿Deseas instalar cron job? [y/N]${NC}"
read -r install_cron

if [[ "$install_cron" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Selecciona la frecuencia:"
    echo "  1) Cada hora"
    echo "  2) Cada 2 horas"
    echo "  3) Cada 6 horas"
    echo "  4) Diario (3:00 AM)"
    echo "  5) Personalizado"
    read -r frequency
    
    case $frequency in
        1)
            cron_schedule="0 * * * *"
            ;;
        2)
            cron_schedule="0 */2 * * *"
            ;;
        3)
            cron_schedule="0 */6 * * *"
            ;;
        4)
            cron_schedule="0 3 * * *"
            ;;
        5)
            echo "Ingresa expresión cron (ej: 0 */4 * * *):"
            read -r cron_schedule
            ;;
        *)
            cron_schedule="0 */2 * * *"
            ;;
    esac
    
    # Agregar a crontab de root
    (crontab -l 2>/dev/null | grep -v "media-organizer"; echo "$cron_schedule /usr/bin/python3 $INSTALL_DIR/auto_organizer.py >> $LOG_DIR/cron.log 2>&1") | crontab -
    
    echo -e "${GREEN}✓ Cron job instalado: $cron_schedule${NC}"
fi

echo ""
echo -e "${GREEN}=== Instalación Completa ===${NC}"
echo ""
echo "Archivos instalados en:"
echo "  - Programa: $INSTALL_DIR/"
echo "  - Config: $CONFIG_DIR/config.yaml"
echo "  - Logs: $LOG_DIR/"
echo ""
echo -e "${YELLOW}SIGUIENTE PASO:${NC}"
echo "  1. Edita la configuración:"
echo "     sudo nano $CONFIG_DIR/config.yaml"
echo ""
echo "  2. Prueba en modo dry-run:"
echo "     sudo python3 $INSTALL_DIR/auto_organizer.py"
echo ""
echo "  3. Si está bien, desactiva dry_run en config.yaml"
echo ""
echo -e "${GREEN}Comandos útiles:${NC}"
echo "  - Ver logs: tail -f $LOG_DIR/organizer.log"
echo "  - Ejecutar manualmente: sudo python3 $INSTALL_DIR/auto_organizer.py"
if [[ "$install_systemd" =~ ^[Yy]$ ]]; then
    echo "  - Estado timer: systemctl status media-organizer.timer"
    echo "  - Ver historial: systemctl list-timers media-organizer.timer"
fi
echo ""
