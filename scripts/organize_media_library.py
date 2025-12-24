#!/usr/bin/env python3
"""
Script para organizar biblioteca de películas y series.
Crea estructura de carpetas compatible con Jellyfin/Plex/Emby.

Estructura objetivo:
- Movies/Nombre Película (Año)/archivo.mkv + metadata
- Series/Nombre Serie/Season XX/episodios
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
import json


class MediaLibraryOrganizer:
    def __init__(self, movies_path, series_path, dry_run=True):
        self.movies_path = Path(movies_path)
        self.series_path = Path(series_path)
        self.dry_run = dry_run
        
        self.operations_log = []
        self.errors_log = []
        
        # Extensiones válidas
        self.video_extensions = ['.mkv', '.mp4', '.avi', '.m4v', '.mov']
        self.metadata_extensions = ['.jpg', '.jpeg', '.png', '.nfo', '.srt', '.sub', '.idx']
        
    def clean_movie_title(self, filename):
        """Extrae y limpia el título de la película."""
        name = filename
        
        # Remover extensión
        for ext in self.video_extensions:
            name = name.replace(ext, '')
        
        # Remover calidades y códecs
        patterns_to_remove = [
            r'\b(1080p|2160p|4K|720p|480p|UHD|HDR|HDR10|DV)\b',
            r'\b(WEB-DL|BluRay|BDRip|REMUX|WEBRip|HDTS|BD|BDRIP)\b',
            r'\b(DD5\.1|DDP5\.1|TrueHD|Atmos|AC3|AAC|5\.1|7\.1|2\.0)\b',
            r'\b(H\.?264|H\.?265|x264|x265|HEVC)\b',
            r'\b(DUAL|Latino|English|Español|Castellano|Multi|Subs?)\b',
            r'\b(AMZN|NF|ATVP|APTV|DSNP|MA|HBO|ChileBT)\b',
            r'\b(EXTENDED|UNRATED|Uncut|REMASTERED|IMAX|CLEAN|LINE|Full)\b',
            r'-[A-Z]{2,}$',
            r'\[.*?\]',
        ]
        
        for pattern in patterns_to_remove:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
        
        # Limpiar caracteres
        name = name.replace('.', ' ').replace('_', ' ').replace('-', ' ')
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def extract_year(self, filename):
        """Extrae el año de la película."""
        year_patterns = [
            r'\((\d{4})\)',
            r'\.(\d{4})\.',
            r'\s(\d{4})\s',
            r'\.(\d{4})$',
            r'\s(\d{4})$',
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, filename)
            if match:
                year = int(match.group(1))
                if 1900 <= year <= 2030:
                    return year
        return None
    
    def create_movie_folder_name(self, title, year):
        """Crea el nombre de carpeta para una película."""
        # Limpiar título
        clean_title = re.sub(r'[<>:"/\\|?*]', '', title)
        clean_title = clean_title.strip()
        
        if year:
            return f"{clean_title} ({year})"
        return clean_title
    
    def find_related_files(self, video_file):
        """Encuentra archivos de metadata relacionados con la película."""
        video_path = Path(video_file)
        base_name = video_path.stem
        parent_dir = video_path.parent
        
        related_files = []
        
        # Buscar archivos con el mismo nombre base
        for file in parent_dir.iterdir():
            if file.is_file() and file != video_path:
                file_stem = file.stem
                
                # Verificar si el archivo está relacionado
                # Puede ser: nombre-poster.jpg, nombre-backdrop.jpg, etc.
                if file_stem.startswith(base_name):
                    related_files.append(file)
        
        return related_files
    
    def organize_movies(self):
        """Organiza todas las películas en carpetas individuales."""
        print("=" * 80)
        print("🎬 ORGANIZANDO PELÍCULAS")
        print("=" * 80)
        print(f"Modo: {'SIMULACIÓN' if self.dry_run else 'EJECUCIÓN REAL'}")
        print()
        
        if not self.movies_path.exists():
            print(f"❌ Error: La ruta {self.movies_path} no existe")
            return
        
        # Buscar archivos de video sueltos
        video_files = []
        for ext in self.video_extensions:
            video_files.extend(self.movies_path.glob(f'*{ext}'))
        
        print(f"📁 Archivos de video encontrados: {len(video_files)}")
        print()
        
        organized_count = 0
        skipped_count = 0
        error_count = 0
        
        for video_file in sorted(video_files):
            try:
                # Extraer título y año
                clean_title = self.clean_movie_title(video_file.name)
                year = self.extract_year(video_file.name)
                
                if not year:
                    print(f"⚠️  Sin año: {video_file.name}")
                    self.errors_log.append({
                        'file': str(video_file),
                        'error': 'No se pudo extraer el año'
                    })
                    skipped_count += 1
                    continue
                
                # Crear nombre de carpeta
                folder_name = self.create_movie_folder_name(clean_title, year)
                target_folder = self.movies_path / folder_name
                
                # Si la carpeta ya existe, puede ser que ya esté organizada
                if target_folder.exists():
                    print(f"⏭️  Ya existe: {folder_name}")
                    skipped_count += 1
                    continue
                
                print(f"📦 {video_file.name}")
                print(f"   → {folder_name}/")
                
                # Buscar archivos relacionados
                related_files = self.find_related_files(video_file)
                
                if related_files:
                    print(f"   📎 Archivos relacionados: {len(related_files)}")
                
                # Crear operación
                operation = {
                    'type': 'movie',
                    'source_video': str(video_file),
                    'target_folder': str(target_folder),
                    'related_files': [str(f) for f in related_files],
                    'title': clean_title,
                    'year': year
                }
                
                # Ejecutar o simular
                if not self.dry_run:
                    # Obtener permisos del directorio padre
                    parent_stat = self.movies_path.stat()
                    parent_uid = parent_stat.st_uid
                    parent_gid = parent_stat.st_gid
                    parent_mode = parent_stat.st_mode
                    
                    # Crear carpeta
                    target_folder.mkdir(exist_ok=True)
                    
                    # Establecer permisos y propietario igual que el directorio padre
                    try:
                        os.chown(str(target_folder), parent_uid, parent_gid)
                        os.chmod(str(target_folder), parent_mode)
                    except PermissionError:
                        pass  # Si no hay permisos, continuar
                    
                    # Mover video
                    target_video = target_folder / video_file.name
                    shutil.move(str(video_file), str(target_video))
                    
                    # Mover archivos relacionados
                    for related_file in related_files:
                        # Renombrar metadata para que sea más simple
                        new_name = related_file.name
                        
                        # Simplificar nombres: titulo-poster.jpg → poster.jpg
                        if '-poster' in new_name.lower():
                            new_name = 'poster' + related_file.suffix
                        elif '-backdrop' in new_name.lower() or '-landscape' in new_name.lower():
                            new_name = 'backdrop' + related_file.suffix
                        elif '-logo' in new_name.lower():
                            new_name = 'logo' + related_file.suffix
                        elif related_file.suffix == '.nfo':
                            new_name = 'movie.nfo'
                        
                        target_related = target_folder / new_name
                        shutil.move(str(related_file), str(target_related))
                    
                    print(f"   ✅ Movida exitosamente")
                else:
                    print(f"   🔵 Simulación - no se movió")
                
                self.operations_log.append(operation)
                organized_count += 1
                print()
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                self.errors_log.append({
                    'file': str(video_file),
                    'error': str(e)
                })
                error_count += 1
                print()
        
        print("=" * 80)
        print("📊 RESUMEN - PELÍCULAS")
        print("=" * 80)
        print(f"✅ Organizadas: {organized_count}")
        print(f"⏭️  Omitidas: {skipped_count}")
        print(f"❌ Errores: {error_count}")
        print()
    
    def organize_series(self):
        """Organiza series verificando que ya tengan estructura correcta."""
        print("=" * 80)
        print("📺 ORGANIZANDO SERIES")
        print("=" * 80)
        print(f"Modo: {'SIMULACIÓN' if self.dry_run else 'EJECUCIÓN REAL'}")
        print()
        
        if not self.series_path.exists():
            print(f"❌ Error: La ruta {self.series_path} no existe")
            return
        
        # Listar todas las carpetas de series
        series_folders = [f for f in self.series_path.iterdir() if f.is_dir()]
        
        print(f"📁 Series encontradas: {len(series_folders)}")
        print()
        
        well_organized = 0
        needs_organization = 0
        
        for series_folder in sorted(series_folders):
            print(f"📺 {series_folder.name}")
            
            # Verificar si tiene estructura de temporadas
            season_folders = list(series_folder.glob('[Ss]eason*')) + \
                           list(series_folder.glob('[Ss][0-9]*')) + \
                           list(series_folder.glob('[Tt]emp*'))
            
            # Buscar archivos de video en la raíz
            video_files = []
            for ext in self.video_extensions:
                video_files.extend(series_folder.glob(f'*{ext}'))
            
            if season_folders:
                print(f"   ✅ Ya tiene {len(season_folders)} temporada(s) organizadas")
                well_organized += 1
            elif video_files:
                print(f"   ⚠️  Archivos sueltos: {len(video_files)}")
                print(f"   💡 Requiere organización manual por temporadas")
                needs_organization += 1
            else:
                # Verificar si tiene subcarpetas que podrían ser temporadas
                subdirs = [d for d in series_folder.iterdir() if d.is_dir()]
                if subdirs:
                    print(f"   📂 Contiene {len(subdirs)} subcarpeta(s):")
                    for subdir in subdirs[:3]:  # Mostrar solo las primeras 3
                        print(f"      - {subdir.name}")
                    if len(subdirs) > 3:
                        print(f"      ... y {len(subdirs) - 3} más")
                    well_organized += 1
                else:
                    print(f"   ⚠️  Carpeta vacía")
            
            print()
        
        print("=" * 80)
        print("📊 RESUMEN - SERIES")
        print("=" * 80)
        print(f"✅ Bien organizadas: {well_organized}")
        print(f"⚠️  Necesitan atención: {needs_organization}")
        print()
    
    def generate_report(self, output_file='organization_report.json'):
        """Genera reporte de las operaciones realizadas."""
        report = {
            'date': datetime.now().isoformat(),
            'dry_run': self.dry_run,
            'movies_path': str(self.movies_path),
            'series_path': str(self.series_path),
            'operations': self.operations_log,
            'errors': self.errors_log,
            'summary': {
                'total_operations': len(self.operations_log),
                'total_errors': len(self.errors_log)
            }
        }
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Reporte guardado: {output_path.absolute()}")
        print()


def main():
    # Configuración
    MOVIES_PATH = "/mnt/PROD/MEDIA/Downloads/Movies"
    SERIES_PATH = "/mnt/PROD/MEDIA/Downloads/Series"
    
    print("=" * 80)
    print("🎬📺 ORGANIZADOR DE BIBLIOTECA MULTIMEDIA")
    print("=" * 80)
    print()
    
    # Modo de ejecución
    import sys
    dry_run = True
    
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        dry_run = False
        print("⚠️  MODO EJECUCIÓN REAL - Se moverán archivos")
        print()
        
        # Pedir confirmación
        response = input("¿Estás seguro de continuar? (escribe 'SI' para confirmar): ")
        if response != 'SI':
            print("❌ Operación cancelada")
            return
        print()
    else:
        print("🔵 MODO SIMULACIÓN - No se moverán archivos")
        print("   Para ejecutar realmente, usa: python3 script.py --execute")
        print()
    
    # Crear organizador
    organizer = MediaLibraryOrganizer(MOVIES_PATH, SERIES_PATH, dry_run=dry_run)
    
    # Organizar películas
    organizer.organize_movies()
    
    # Organizar series
    organizer.organize_series()
    
    # Generar reporte
    organizer.generate_report('media_organization_report.json')
    
    print("=" * 80)
    print("✅ PROCESO COMPLETADO")
    print("=" * 80)
    
    if dry_run:
        print()
        print("💡 Este fue un modo simulación. Para ejecutar:")
        print("   python3 organize_media_library.py --execute")


if __name__ == "__main__":
    main()
