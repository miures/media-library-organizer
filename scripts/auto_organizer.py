#!/usr/bin/env python3
"""
Media Library Organizer - Versión Automatizada
Organiza películas, series y otros medios automáticamente
Compatible con Jellyfin, Plex, Emby
"""

import os
import sys
import re
import shutil
import logging
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import hashlib


class MediaOrganizerAutomated:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.stats = {
            'processed': 0,
            'moved': 0,
            'errors': 0,
            'duplicates': 0,
            'skipped': 0
        }
        
    def load_config(self, config_path: str) -> dict:
        """Carga la configuración desde YAML"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        """Configura el sistema de logging"""
        log_config = self.config.get('logging', {})
        
        if not log_config.get('enabled', True):
            logging.basicConfig(level=logging.WARNING)
            return
        
        log_file = Path(log_config.get('log_file', '/var/log/media-organizer/organizer.log'))
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        log_level = getattr(logging, log_config.get('log_level', 'INFO'))
        
        # Configurar formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para archivo
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Configurar logger
        self.logger = logging.getLogger('MediaOrganizer')
        self.logger.setLevel(log_level)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def clean_title(self, filename: str) -> str:
        """Limpia el título del archivo"""
        name = filename
        
        # Remover extensión
        video_exts = self.config['settings']['video_extensions']
        for ext in video_exts:
            name = name.replace(ext, '')
        
        # Patrones a remover
        patterns = [
            r'\b(1080p|2160p|4K|720p|480p|UHD|HDR|HDR10|HDR10\+|DV|Dolby.?Vision)\b',
            r'\b(WEB-?DL|BluRay|BDRip|REMUX|WEBRip|HDTS|BD|BDRIP|DVD-?Rip)\b',
            r'\b(DD5\.1|DDP5\.1|TrueHD|Atmos|AC3|AAC|5\.1|7\.1|2\.0|DTS)\b',
            r'\b(H\.?264|H\.?265|x264|x265|HEVC|AVC|10bit|8bit)\b',
            r'\b(DUAL|Latino|English|Español|Castellano|Multi|Subs?)\b',
            r'\b(AMZN|NF|ATVP|APTV|DSNP|MA|HBO|HMAX|HULU|ChileBT)\b',
            r'\b(EXTENDED|UNRATED|Uncut|REMASTERED|IMAX|CLEAN|LINE|Full)\b',
            r'\b(Director.?s?.?Cut|Theatrical|Special.?Edition)\b',
            r'-[A-Z0-9]{2,}$',
            r'\[.*?\]',
            r'\(.*?(Blu-?ray|WEB|REMUX).*?\)',
        ]
        
        for pattern in patterns:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
        
        # Limpiar caracteres
        name = name.replace('.', ' ').replace('_', ' ').replace('-', ' ')
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def extract_year(self, filename: str) -> Optional[int]:
        """Extrae el año del nombre del archivo"""
        patterns = [
            r'\((\d{4})\)',
            r'\.(\d{4})\.',
            r'\s(\d{4})\s',
            r'\.(\d{4})$',
            r'\s(\d{4})$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                year = int(match.group(1))
                if 1900 <= year <= 2035:
                    return year
        return None
    
    def get_file_hash(self, filepath: Path, chunk_size: int = 8192) -> str:
        """Calcula hash MD5 de un archivo"""
        md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                md5.update(chunk)
        return md5.hexdigest()
    
    def is_valid_video(self, filepath: Path) -> bool:
        """Verifica si es un archivo de video válido"""
        video_exts = self.config['settings']['video_extensions']
        min_size_mb = self.config['settings'].get('min_file_size_mb', 100)
        
        if filepath.suffix.lower() not in video_exts:
            return False
        
        size_mb = filepath.stat().st_size / (1024 * 1024)
        if size_mb < min_size_mb:
            self.logger.debug(f"Archivo muy pequeño ({size_mb:.1f}MB): {filepath.name}")
            return False
        
        return True
    
    def find_related_files(self, video_file: Path) -> List[Path]:
        """Encuentra archivos relacionados (subtítulos, NFO, etc)"""
        related = []
        base_name = video_file.stem
        parent_dir = video_file.parent
        
        metadata_exts = self.config['settings']['metadata_extensions']
        
        for file in parent_dir.iterdir():
            if file == video_file or not file.is_file():
                continue
            
            # Archivos con el mismo nombre base
            if file.stem == base_name or file.stem.startswith(base_name):
                if file.suffix.lower() in metadata_exts:
                    related.append(file)
        
        return related
    
    def organize_movie(self, video_file: Path, destination_root: Path) -> bool:
        """Organiza una película en la estructura correcta"""
        try:
            title = self.clean_title(video_file.stem)
            year = self.extract_year(video_file.name)
            
            # Crear nombre de carpeta
            if year:
                folder_name = f"{title} ({year})"
            else:
                folder_name = title
            
            # Limpiar caracteres inválidos
            folder_name = re.sub(r'[<>:"/\\|?*]', '', folder_name).strip()
            
            dest_folder = destination_root / folder_name
            
            # Verificar si ya existe
            if dest_folder.exists():
                existing_videos = list(dest_folder.glob('*' + video_file.suffix))
                if existing_videos:
                    self.logger.info(f"Ya existe: {folder_name}")
                    self.stats['skipped'] += 1
                    return False
            
            # Modo dry-run
            if self.config['settings']['dry_run']:
                self.logger.info(f"[DRY-RUN] Movería {video_file.name} -> {dest_folder}")
                self.stats['processed'] += 1
                return True
            
            # Crear carpeta destino
            dest_folder.mkdir(parents=True, exist_ok=True)
            
            # Mover/copiar archivo de video
            dest_video = dest_folder / video_file.name
            move_or_copy = self.config['settings'].get('move_or_copy', 'move')
            
            if move_or_copy == 'copy':
                shutil.copy2(video_file, dest_video)
            else:
                shutil.move(str(video_file), str(dest_video))
            
            self.logger.info(f"✓ {video_file.name} -> {folder_name}")
            
            # Mover archivos relacionados
            related_files = self.find_related_files(video_file)
            for related in related_files:
                dest_related = dest_folder / related.name
                if move_or_copy == 'copy':
                    shutil.copy2(related, dest_related)
                else:
                    shutil.move(str(related), str(dest_related))
            
            self.stats['moved'] += 1
            self.stats['processed'] += 1
            return True
            
        except Exception as e:
            self.logger.error(f"Error procesando {video_file.name}: {e}")
            self.stats['errors'] += 1
            return False
    
    def process_directory(self, category: str, source: Path, destination: Path):
        """Procesa un directorio completo"""
        self.logger.info(f"Procesando categoría: {category}")
        self.logger.info(f"  Origen: {source}")
        self.logger.info(f"  Destino: {destination}")
        
        if not source.exists():
            self.logger.warning(f"El directorio origen no existe: {source}")
            return
        
        destination.mkdir(parents=True, exist_ok=True)
        
        # Buscar archivos de video
        video_files = []
        for ext in self.config['settings']['video_extensions']:
            video_files.extend(source.rglob(f'*{ext}'))
        
        self.logger.info(f"  Encontrados {len(video_files)} archivos de video")
        
        for video_file in video_files:
            if not self.is_valid_video(video_file):
                continue
            
            if category in ['movies', 'anime', 'documentaries']:
                self.organize_movie(video_file, destination)
            elif category in ['series']:
                # TODO: Implementar organización de series
                self.logger.debug(f"Series aún no implementado: {video_file.name}")
    
    def run(self):
        """Ejecuta el organizador para todos los directorios configurados"""
        self.logger.info("=" * 60)
        self.logger.info("Iniciando Media Library Organizer")
        self.logger.info("=" * 60)
        
        start_time = datetime.now()
        
        directories = self.config.get('directories', {})
        
        for category, config in directories.items():
            if not config.get('enabled', False):
                self.logger.debug(f"Categoría deshabilitada: {category}")
                continue
            
            if not config.get('auto_organize', False):
                self.logger.debug(f"Auto-organizar deshabilitado: {category}")
                continue
            
            source = Path(config['source'])
            destination = Path(config['destination'])
            
            self.process_directory(category, source, destination)
        
        # Resumen
        duration = datetime.now() - start_time
        self.logger.info("=" * 60)
        self.logger.info("Resumen de ejecución:")
        self.logger.info(f"  Procesados: {self.stats['processed']}")
        self.logger.info(f"  Movidos: {self.stats['moved']}")
        self.logger.info(f"  Saltados: {self.stats['skipped']}")
        self.logger.info(f"  Errores: {self.stats['errors']}")
        self.logger.info(f"  Duración: {duration}")
        self.logger.info("=" * 60)
        
        return self.stats


def main():
    # Buscar archivo de configuración
    config_paths = [
        'config.yaml',
        '/etc/media-organizer/config.yaml',
        str(Path.home() / '.config/media-organizer/config.yaml'),
        str(Path(__file__).parent.parent / 'config.yaml'),
    ]
    
    config_file = None
    for path in config_paths:
        if Path(path).exists():
            config_file = path
            break
    
    if not config_file:
        print("Error: No se encontró archivo de configuración (config.yaml)")
        print(f"Buscado en: {', '.join(config_paths)}")
        sys.exit(1)
    
    try:
        organizer = MediaOrganizerAutomated(config_file)
        organizer.run()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
