#!/usr/bin/env python3
"""
Script para mover películas duplicadas a carpeta de Duplicados.
Mantiene la mejor calidad en Movies y mueve las versiones inferiores.
"""

import os
import shutil
from pathlib import Path

MOVIES_PATH = "/mnt/PROD/MEDIA/Downloads/Movies"
DUPLICATES_PATH = "/mnt/PROD/MEDIA/Duplicados"

# Lista de películas duplicadas con prioridad (mantener la mejor)
DUPLICATES = {
    "F1 The Movie 2025 (2025)": {
        "keep": "2160p",  # Mantener 4K
        "move": "1080p"   # Mover 1080p
    },
    "Gran Turismo 2023 (2023)": {
        "keep": "2160p",
        "move": "1080p"
    },
    "Napoleon 2024 (2024)": {
        "keep": "4K",
        "move": "1080p"
    },
    "Novocaine 2025 (2025)": {
        "keep": "2160p",
        "move": "1080p"
    },
    "Oppenheimer (2023)": {
        "keep": "DUAL",
        "move": "IMAX"
    },
    "Wonka (2023) (2023)": {
        "keep": "4k",
        "move": "1080p"
    }
}

# Carpetas completas a mover
FULL_FOLDERS_TO_MOVE = [
    "Oppenheimer 2023 (2023)",
    "Wonka 2023 (2023)"
]

def main():
    # Crear carpeta de duplicados
    os.makedirs(DUPLICATES_PATH, exist_ok=True)
    
    # Obtener permisos del directorio padre
    parent_stat = Path("/mnt/PROD/MEDIA").stat()
    os.chown(DUPLICATES_PATH, parent_stat.st_uid, parent_stat.st_gid)
    os.chmod(DUPLICATES_PATH, parent_stat.st_mode)
    
    print("🔍 Moviendo duplicados...")
    print("=" * 60)
    
    moved_count = 0
    
    # Procesar películas con versiones duplicadas
    for folder_name, criteria in DUPLICATES.items():
        folder_path = Path(MOVIES_PATH) / folder_name
        
        if not folder_path.exists():
            continue
        
        print(f"\n📦 {folder_name}")
        
        # Buscar archivos a mover
        files_to_move = []
        for file in folder_path.iterdir():
            if file.is_file() and criteria["move"].lower() in file.name.lower():
                files_to_move.append(file)
        
        if files_to_move:
            # Crear carpeta en Duplicados
            dup_folder = Path(DUPLICATES_PATH) / folder_name
            dup_folder.mkdir(exist_ok=True)
            
            # Mover archivos
            for file in files_to_move:
                dest = dup_folder / file.name
                shutil.move(str(file), str(dest))
                print(f"   ✅ {file.name} → Duplicados")
                moved_count += 1
            
            # Establecer permisos
            os.chown(str(dup_folder), parent_stat.st_uid, parent_stat.st_gid)
            os.chmod(str(dup_folder), parent_stat.st_mode)
    
    # Mover carpetas completas
    for folder_name in FULL_FOLDERS_TO_MOVE:
        folder_path = Path(MOVIES_PATH) / folder_name
        
        if not folder_path.exists():
            continue
        
        print(f"\n📁 {folder_name} (carpeta completa)")
        
        # Crear carpeta en Duplicados
        dup_folder = Path(DUPLICATES_PATH) / folder_name
        dup_folder.mkdir(exist_ok=True)
        
        # Mover todos los archivos
        for file in folder_path.iterdir():
            if file.is_file():
                dest = dup_folder / file.name
                shutil.move(str(file), str(dest))
                print(f"   ✅ {file.name}")
                moved_count += 1
        
        # Eliminar carpeta vacía
        try:
            folder_path.rmdir()
            print(f"   🗑️  Carpeta vacía eliminada")
        except:
            pass
        
        # Establecer permisos
        os.chown(str(dup_folder), parent_stat.st_uid, parent_stat.st_gid)
        os.chmod(str(dup_folder), parent_stat.st_mode)
    
    print("\n" + "=" * 60)
    print(f"✅ Proceso completado")
    print(f"📊 Archivos movidos: {moved_count}")
    
    # Mostrar resumen
    dup_folders = [d for d in Path(DUPLICATES_PATH).iterdir() if d.is_dir()]
    print(f"📁 Películas en Duplicados: {len(dup_folders)}")
    
    # Calcular espacio
    total_size = 0
    for folder in dup_folders:
        for file in folder.rglob('*'):
            if file.is_file():
                total_size += file.stat().st_size
    
    size_gb = total_size / (1024**3)
    print(f"💾 Espacio en Duplicados: {size_gb:.2f} GB")

if __name__ == "__main__":
    main()
