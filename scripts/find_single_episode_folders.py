#!/usr/bin/env python3
"""
Script para encontrar carpetas de anime con un solo capítulo/archivo.
Útil para identificar series incompletas o películas mal categorizadas.
"""

import os
import sys
import yaml
from pathlib import Path

# Extensiones de video válidas
VIDEO_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.m4v', '.mov', '.wmv', '.flv', '.webm'}

def load_config():
    """Cargar configuración desde config.yaml"""
    config_path = Path(__file__).parent.parent / 'config.yaml'
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return None

def count_video_files(directory: Path) -> int:
    """Contar archivos de video en un directorio (recursivo)"""
    count = 0
    try:
        for item in directory.rglob('*'):
            if item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS:
                count += 1
    except PermissionError:
        pass
    return count

def find_single_episode_folders(anime_dir: str, max_files: int = 1):
    """
    Encontrar carpetas que contienen solo 1 archivo de video (o hasta max_files).
    
    Args:
        anime_dir: Ruta al directorio de anime
        max_files: Número máximo de archivos para considerar (default: 1)
    """
    anime_path = Path(anime_dir)
    
    if not anime_path.exists():
        print(f"❌ Error: El directorio no existe: {anime_dir}")
        print("   Verifica que el directorio esté montado correctamente.")
        sys.exit(1)
    
    if not anime_path.is_dir():
        print(f"❌ Error: La ruta no es un directorio: {anime_dir}")
        sys.exit(1)
    
    print(f"🔍 Buscando en: {anime_dir}")
    print(f"📋 Mostrando carpetas con {max_files} archivo(s) o menos\n")
    print("=" * 70)
    
    results = []
    
    # Iterar sobre subdirectorios de primer nivel
    for subdir in sorted(anime_path.iterdir()):
        if subdir.is_dir():
            video_count = count_video_files(subdir)
            if 0 < video_count <= max_files:
                results.append((subdir.name, video_count))
    
    if not results:
        print("✅ No se encontraron carpetas con solo 1 archivo de video.")
    else:
        print(f"📁 Carpetas con {max_files} archivo(s) o menos ({len(results)} encontradas):\n")
        for folder_name, count in results:
            emoji = "📄" if count == 1 else "📑"
            print(f"  {emoji} {folder_name} ({count} archivo{'s' if count > 1 else ''})")
    
    print("\n" + "=" * 70)
    print(f"📊 Total de carpetas encontradas: {len(results)}")
    
    return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Encontrar carpetas de anime con pocos archivos/capítulos'
    )
    parser.add_argument(
        '-d', '--directory',
        help='Directorio de anime (usa config.yaml si no se especifica)'
    )
    parser.add_argument(
        '-m', '--max-files',
        type=int,
        default=1,
        help='Número máximo de archivos para mostrar (default: 1)'
    )
    parser.add_argument(
        '--show-files',
        action='store_true',
        help='Mostrar nombres de los archivos encontrados'
    )
    
    args = parser.parse_args()
    
    # Determinar directorio
    anime_dir = args.directory
    
    if not anime_dir:
        config = load_config()
        if config and 'directories' in config and 'anime' in config['directories']:
            anime_dir = config['directories']['anime']['source']
            print(f"📖 Usando directorio desde config.yaml: {anime_dir}\n")
        else:
            print("❌ Error: No se especificó directorio y no se encontró config.yaml")
            sys.exit(1)
    
    results = find_single_episode_folders(anime_dir, args.max_files)
    
    # Mostrar archivos si se solicita
    if args.show_files and results:
        print("\n📝 Detalle de archivos:\n")
        anime_path = Path(anime_dir)
        for folder_name, _ in results:
            folder_path = anime_path / folder_name
            print(f"📁 {folder_name}:")
            for item in folder_path.rglob('*'):
                if item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS:
                    print(f"   └─ {item.name}")
            print()

if __name__ == '__main__':
    main()
