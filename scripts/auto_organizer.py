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
import xml.etree.ElementTree as ET
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
    
    def detect_series_info(self, filename: str) -> Optional[Dict[str, any]]:
        """Detecta si un archivo es una serie y extrae información"""
        # Patrones para detectar episodios (orden importa: más específicos primero)
        patterns = [
            # S01E01, S1E1, etc.
            r'[Ss](\d{1,2})[Ee](\d{1,3})',
            # 1x01, 1x1, etc.
            r'(\d{1,2})x(\d{1,3})',
            # Nombre Serie 01 al final (debe ir antes del patrón general)
            r'\s+(\d{1,3})(?:v\d+)?$',
            # - 01 -, _01_, etc.
            r'[\s\-_](\d{1,3})[\s\-_]',
            # Episode 01, EP01, etc.
            r'[Ee]pisode[\s\-_]?(\d{1,3})',
            r'[Ee][Pp][\s\-_]?(\d{1,3})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                groups = match.groups()
                if len(groups) == 2:  # Tiene temporada y episodio
                    season = int(groups[0])
                    episode = int(groups[1])
                elif len(groups) == 1:  # Solo episodio
                    season = 1
                    episode = int(groups[0])
                else:
                    continue
                
                # Extraer el nombre de la serie (antes del patrón)
                series_name = filename[:match.start()]
                series_name = self.clean_title(series_name)
                
                return {
                    'series_name': series_name,
                    'season': season,
                    'episode': episode,
                    'is_series': True
                }
        
        return None
    
    def create_tvshow_nfo(self, series_name: str, dest_folder: Path) -> bool:
        """Crea archivo tvshow.nfo para la serie"""
        try:
            nfo_path = dest_folder / "tvshow.nfo"
            
            # Si ya existe, no sobreescribir
            if nfo_path.exists():
                return True
            
            # Crear estructura XML
            tvshow = ET.Element('tvshow')
            
            title = ET.SubElement(tvshow, 'title')
            title.text = series_name
            
            plot = ET.SubElement(tvshow, 'plot')
            plot.text = f"Serie de anime: {series_name}"
            
            # Agregar año si se detecta
            year_match = re.search(r'\b(19|20)\d{2}\b', series_name)
            if year_match:
                year_elem = ET.SubElement(tvshow, 'year')
                year_elem.text = year_match.group(0)
                premiered = ET.SubElement(tvshow, 'premiered')
                premiered.text = f"{year_match.group(0)}-01-01"
            
            genre = ET.SubElement(tvshow, 'genre')
            genre.text = "Anime"
            
            # Crear árbol y escribir
            tree = ET.ElementTree(tvshow)
            ET.indent(tree, space="  ")
            tree.write(nfo_path, encoding='utf-8', xml_declaration=True)
            
            self.logger.debug(f"Creado tvshow.nfo para {series_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creando tvshow.nfo para {series_name}: {e}")
            return False
    
    def create_episode_nfo(self, video_file: Path, series_info: Dict, dest_folder: Path) -> bool:
        """Crea archivo NFO para un episodio"""
        try:
            nfo_path = dest_folder / f"{video_file.stem}.nfo"
            
            # Si ya existe, no sobreescribir
            if nfo_path.exists():
                return True
            
            # Crear estructura XML
            episodedetails = ET.Element('episodedetails')
            
            title = ET.SubElement(episodedetails, 'title')
            title.text = f"{series_info['series_name']} - Episodio {series_info['episode']}"
            
            showtitle = ET.SubElement(episodedetails, 'showtitle')
            showtitle.text = series_info['series_name']
            
            season = ET.SubElement(episodedetails, 'season')
            season.text = str(series_info['season'])
            
            episode = ET.SubElement(episodedetails, 'episode')
            episode.text = str(series_info['episode'])
            
            plot = ET.SubElement(episodedetails, 'plot')
            plot.text = f"Episodio {series_info['episode']} de {series_info['series_name']}"
            
            # Crear árbol y escribir
            tree = ET.ElementTree(episodedetails)
            ET.indent(tree, space="  ")
            tree.write(nfo_path, encoding='utf-8', xml_declaration=True)
            
            self.logger.debug(f"Creado {nfo_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creando episode.nfo para {video_file.name}: {e}")
            return False
    
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
    
    def organize_series(self, video_file: Path, destination_root: Path) -> bool:
        """Organiza una serie agrupando episodios por nombre de serie"""
        try:
            series_info = self.detect_series_info(video_file.name)
            
            # Si no se detecta como serie, tratarlo como película
            if not series_info:
                return self.organize_movie(video_file, destination_root)
            
            series_name = series_info['series_name']
            season = series_info['season']
            episode = series_info['episode']
            
            # Limpiar caracteres inválidos
            series_name = re.sub(r'[<>:"/\\|?*]', '', series_name).strip()
            
            # Crear estructura: Series/SeriesName/ o Series/SeriesName/Season 01/
            dest_folder = destination_root / series_name
            
            # Verificar si ya existe el archivo
            if dest_folder.exists():
                # Buscar si ya existe un archivo similar
                existing_pattern = f"*{season:02d}*{episode:02d}*{video_file.suffix}"
                existing_files = list(dest_folder.glob(existing_pattern))
                if not existing_files:
                    # Buscar sin formato de ceros
                    existing_pattern2 = f"*{season}*{episode:02d}*{video_file.suffix}"
                    existing_files = list(dest_folder.glob(existing_pattern2))
                
                if existing_files:
                    self.logger.info(f"Ya existe: {series_name} S{season:02d}E{episode:02d}")
                    self.stats['skipped'] += 1
                    return False
            
            # Modo dry-run
            if self.config['settings']['dry_run']:
                nfo_msg = ""
                if self.config['settings'].get('create_nfo_files', False):
                    nfo_msg = " + NFO"
                self.logger.info(f"[DRY-RUN] Movería {video_file.name} -> {dest_folder}/{nfo_msg}")
                self.stats['processed'] += 1
                return True
            
            # Crear carpeta destino
            dest_folder.mkdir(parents=True, exist_ok=True)
            
            # Crear tvshow.nfo si está habilitado
            if self.config['settings'].get('create_nfo_files', False):
                self.create_tvshow_nfo(series_name, dest_folder)
            
            # Mover/copiar archivo de video
            dest_video = dest_folder / video_file.name
            move_or_copy = self.config['settings'].get('move_or_copy', 'move')
            
            if move_or_copy == 'copy':
                shutil.copy2(video_file, dest_video)
            else:
                shutil.move(str(video_file), str(dest_video))
            
            self.logger.info(f"✓ {video_file.name} -> {series_name}/")
            
            # Crear episode.nfo si está habilitado
            if self.config['settings'].get('create_nfo_files', False):
                self.create_episode_nfo(video_file, series_info, dest_folder)
            
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
            self.logger.error(f"Error procesando serie {video_file.name}: {e}")
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
            
            if category in ['movies', 'documentaries']:
                self.organize_movie(video_file, destination)
            elif category in ['series', 'anime']:
                self.organize_series(video_file, destination)
    
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
