#!/usr/bin/env python3
"""
Script para detectar películas duplicadas en el repositorio de medios.
Detecta duplicados basándose en el título y año de la película.
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import json


class MovieDuplicateDetector:
    def __init__(self, movies_path):
        self.movies_path = Path(movies_path)
        self.movies_db = defaultdict(list)
        self.duplicates = defaultdict(list)
        
    def clean_title(self, filename):
        """Extrae y limpia el título de la película del nombre del archivo."""
        # Remover extensión
        name = filename.replace('.mkv', '').replace('.mp4', '').replace('.avi', '')
        
        # Patrones comunes para limpiar
        # Remueve calidades: 1080p, 2160p, 4K, HDR, etc.
        name = re.sub(r'\b(1080p|2160p|4K|720p|480p|UHD|HDR|HDR10|DV)\b', '', name, flags=re.IGNORECASE)
        
        # Remueve códecs y formatos
        name = re.sub(r'\b(WEB-DL|BluRay|BDRip|REMUX|WEBRip|HDTS|BD|BDRIP)\b', '', name, flags=re.IGNORECASE)
        
        # Remueve audio
        name = re.sub(r'\b(DD5\.1|DDP5\.1|TrueHD|Atmos|AC3|AAC|5\.1|7\.1|2\.0)\b', '', name, flags=re.IGNORECASE)
        
        # Remueve códecs de video
        name = re.sub(r'\b(H\.?264|H\.?265|x264|x265|HEVC)\b', '', name, flags=re.IGNORECASE)
        
        # Remueve idiomas
        name = re.sub(r'\b(DUAL|Latino|English|Español|Castellano|Multi|Subs?)\b', '', name, flags=re.IGNORECASE)
        
        # Remueve grupos de release
        name = re.sub(r'-[A-Z]{2,}$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\[.*?\]', '', name)
        name = re.sub(r'\(.*?DUAL.*?\)', '', name, flags=re.IGNORECASE)
        
        # Remueve plataformas
        name = re.sub(r'\b(AMZN|NF|ATVP|APTV|DSNP|MA|HBO)\b', '', name, flags=re.IGNORECASE)
        
        # Remueve palabras extras
        name = re.sub(r'\b(EXTENDED|UNRATED|Uncut|REMASTERED|IMAX|CLEAN|LINE)\b', '', name, flags=re.IGNORECASE)
        
        # Limpia puntos, guiones y espacios múltiples
        name = name.replace('.', ' ').replace('_', ' ').replace('-', ' ')
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def extract_year(self, filename):
        """Extrae el año de la película."""
        # Buscar año entre paréntesis o después del título
        year_patterns = [
            r'\((\d{4})\)',  # (2024)
            r'\.(\d{4})\.',  # .2024.
            r'\s(\d{4})\s',  # 2024
            r'\.(\d{4})$',   # .2024 al final
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, filename)
            if match:
                year = int(match.group(1))
                if 1900 <= year <= 2030:  # Validar rango razonable
                    return year
        return None
    
    def normalize_title(self, title):
        """Normaliza el título para comparación."""
        # Convertir a minúsculas
        title = title.lower()
        
        # Remover artículos comunes
        title = re.sub(r'^(the|la|el|los|las|a|an)\s+', '', title)
        
        # Remover caracteres especiales
        title = re.sub(r'[^\w\s]', '', title)
        
        # Remover espacios múltiples
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title
    
    def get_file_info(self, filepath):
        """Obtiene información detallada del archivo."""
        stat = filepath.stat()
        
        # Detectar calidad
        quality = 'SD'
        if '2160p' in filepath.name or '4K' in filepath.name.upper():
            quality = '4K'
        elif '1080p' in filepath.name:
            quality = '1080p'
        elif '720p' in filepath.name:
            quality = '720p'
        
        # Detectar HDR
        has_hdr = bool(re.search(r'\b(HDR|HDR10|DV|Dolby Vision)\b', filepath.name, re.IGNORECASE))
        
        # Detectar audio
        audio = 'Stereo'
        if re.search(r'\b(Atmos|TrueHD|7\.1)\b', filepath.name, re.IGNORECASE):
            audio = 'Atmos/7.1'
        elif re.search(r'\b(DD5\.1|DDP5\.1|5\.1)\b', filepath.name, re.IGNORECASE):
            audio = '5.1'
        
        # Detectar idioma
        is_dual = 'DUAL' in filepath.name.upper()
        
        return {
            'path': str(filepath),
            'filename': filepath.name,
            'size_bytes': stat.st_size,
            'size_gb': round(stat.st_size / (1024**3), 2),
            'quality': quality,
            'hdr': has_hdr,
            'audio': audio,
            'dual_audio': is_dual,
            'modified': stat.st_mtime
        }
    
    def scan_movies(self):
        """Escanea el directorio de películas."""
        print(f"🔍 Escaneando: {self.movies_path}")
        print("=" * 80)
        
        # Buscar archivos .mkv sueltos
        mkv_files = list(self.movies_path.glob('*.mkv'))
        mp4_files = list(self.movies_path.glob('*.mp4'))
        avi_files = list(self.movies_path.glob('*.avi'))
        
        all_files = mkv_files + mp4_files + avi_files
        
        print(f"📁 Archivos encontrados: {len(all_files)}")
        print()
        
        for filepath in all_files:
            # Extraer título y año
            clean_title = self.clean_title(filepath.name)
            year = self.extract_year(filepath.name)
            
            if not year:
                print(f"⚠️  Sin año detectado: {filepath.name}")
                continue
            
            # Normalizar título para comparación
            normalized_title = self.normalize_title(clean_title)
            
            # Crear clave única: título + año
            key = f"{normalized_title}|{year}"
            
            # Obtener información del archivo
            file_info = self.get_file_info(filepath)
            file_info['clean_title'] = clean_title
            file_info['year'] = year
            file_info['normalized_title'] = normalized_title
            
            self.movies_db[key].append(file_info)
        
        print(f"✅ Escaneo completado: {len(self.movies_db)} películas únicas identificadas")
        print()
    
    def find_duplicates(self):
        """Encuentra duplicados."""
        print("🔎 Buscando duplicados...")
        print("=" * 80)
        
        for key, movies in self.movies_db.items():
            if len(movies) > 1:
                self.duplicates[key] = movies
        
        print(f"🎬 Duplicados encontrados: {len(self.duplicates)} películas")
        print()
    
    def display_duplicates(self):
        """Muestra los duplicados encontrados."""
        if not self.duplicates:
            print("✨ No se encontraron películas duplicadas!")
            return
        
        print("=" * 80)
        print("📋 REPORTE DE PELÍCULAS DUPLICADAS")
        print("=" * 80)
        print()
        
        total_wasted_space = 0
        duplicate_count = 0
        
        for key, movies in sorted(self.duplicates.items()):
            duplicate_count += 1
            title_parts = key.split('|')
            normalized_title = title_parts[0]
            year = title_parts[1]
            
            print(f"🎬 Película #{duplicate_count}: {movies[0]['clean_title']} ({year})")
            print(f"   Copias encontradas: {len(movies)}")
            print()
            
            # Ordenar por calidad y tamaño
            sorted_movies = sorted(movies, key=lambda x: (
                x['quality'] != '4K',
                not x['hdr'],
                not x['dual_audio'],
                x['audio'] != 'Atmos/7.1',
                -x['size_bytes']
            ))
            
            best_quality = sorted_movies[0]
            
            for idx, movie in enumerate(sorted_movies, 1):
                is_best = movie == best_quality
                marker = "⭐ MEJOR" if is_best else "   "
                
                print(f"   {marker} Versión {idx}:")
                print(f"        📄 Archivo: {movie['filename']}")
                print(f"        💾 Tamaño: {movie['size_gb']} GB")
                print(f"        🎥 Calidad: {movie['quality']}")
                print(f"        ✨ HDR: {'Sí' if movie['hdr'] else 'No'}")
                print(f"        🔊 Audio: {movie['audio']}")
                print(f"        🌐 Dual: {'Sí' if movie['dual_audio'] else 'No'}")
                print()
                
                if not is_best:
                    total_wasted_space += movie['size_bytes']
            
            print("-" * 80)
            print()
        
        print("=" * 80)
        print("📊 RESUMEN")
        print("=" * 80)
        print(f"Total de películas duplicadas: {len(self.duplicates)}")
        print(f"Total de archivos duplicados: {sum(len(m) - 1 for m in self.duplicates.values())}")
        print(f"Espacio desperdiciado: {round(total_wasted_space / (1024**3), 2)} GB")
        print()
    
    def generate_report(self, output_file='duplicate_movies_report.json'):
        """Genera un reporte JSON con los duplicados."""
        from datetime import datetime
        report = {
            'scan_date': datetime.now().isoformat(),
            'movies_path': str(self.movies_path),
            'total_movies': len(self.movies_db),
            'duplicate_movies': len(self.duplicates),
            'duplicates': {}
        }
        
        for key, movies in self.duplicates.items():
            title_parts = key.split('|')
            report['duplicates'][key] = {
                'title': movies[0]['clean_title'],
                'year': movies[0]['year'],
                'copies': movies
            }
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Reporte guardado en: {output_path.absolute()}")
        print()


def main():
    # Configuración
    MOVIES_PATH = "/mnt/PROD/MEDIA/Downloads/Movies"
    
    print("=" * 80)
    print("🎬 DETECTOR DE PELÍCULAS DUPLICADAS")
    print("=" * 80)
    print()
    
    # Crear detector
    detector = MovieDuplicateDetector(MOVIES_PATH)
    
    # Escanear películas
    detector.scan_movies()
    
    # Buscar duplicados
    detector.find_duplicates()
    
    # Mostrar duplicados
    detector.display_duplicates()
    
    # Generar reporte JSON
    detector.generate_report('duplicate_movies_report.json')
    
    print("✅ Proceso completado!")


if __name__ == "__main__":
    main()
