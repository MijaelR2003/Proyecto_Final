import os
import zipfile
import shutil

# Archivos ZIP y carpetas destino
datasets = [
    ("dental_radiography.zip", "dental_radiography"),
    ("panoramic_dental_dataset.zip", "panoramic_dental_dataset"),
    ("panoramic_dental_xray_dataset.zip", "panoramic_dental_xray_dataset")
]

base_dir = os.path.dirname(__file__)

# 1. Extraer ZIPs
for zip_name, folder_name in datasets:
    zip_path = os.path.join(base_dir, zip_name)
    extract_dir = os.path.join(base_dir, folder_name)
    if os.path.exists(zip_path):
        print(f"Extrayendo {zip_name}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print(f"Extraído en {extract_dir}")
    else:
        print(f"No se encontró {zip_name}")

import csv

def organizar_multiclase_dental_radiography(split_folder):
    """
    Organiza imágenes en carpetas multicategoría según _annotations.csv.
    Crea una carpeta por clase y una carpeta 'sano' para imágenes no anotadas.
    split_folder: ruta absoluta a train, test o valid
    """
    csv_path = os.path.join(split_folder, '_annotations.csv')
    images_dir = split_folder
    destino = os.path.join(split_folder, 'organizado')
    os.makedirs(destino, exist_ok=True)
    clases = set()
    img2clases = dict()
    anotadas = set()
    # Leer anotaciones
    if os.path.exists(csv_path):
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                fname = row['filename']
                clase = row['class']
                clases.add(clase)
                anotadas.add(fname)
                if fname not in img2clases:
                    img2clases[fname] = set()
                img2clases[fname].add(clase)
    # Crear carpetas de clase
    for clase in clases:
        os.makedirs(os.path.join(destino, clase), exist_ok=True)
    os.makedirs(os.path.join(destino, 'sano'), exist_ok=True)
    # Copiar imágenes a carpetas de clase
    for fname in os.listdir(images_dir):
        if not fname.lower().endswith(('.jpg','.jpeg','.png')):
            continue
        src = os.path.join(images_dir, fname)
        if fname in img2clases:
            for clase in img2clases[fname]:
                shutil.copy2(src, os.path.join(destino, clase, fname))
        else:
            shutil.copy2(src, os.path.join(destino, 'sano', fname))
    print(f"Organización multiclase terminada en {destino}")

# --- ORGANIZACIÓN MULTICLASE AUTOMÁTICA PARA DENTAL RADIOGRAPHY ---
for split in ['train', 'test', 'valid']:
    split_folder = os.path.join(base_dir, 'dental_radiography', split)
    if os.path.exists(split_folder):
        organizar_multiclase_dental_radiography(split_folder)
    else:
        print(f"No encontrado: {split_folder}")

# --- ORGANIZACIÓN SANO/PATOLÓGICO/SIN ANOTACION PARA PANORAMIC DENTAL DATASET ---
def organizar_panoramic_dental_dataset(base_dir):
    images_dir = os.path.join(base_dir, 'panoramic_dental_dataset', 'images')
    bboxes_caries_dir = os.path.join(base_dir, 'panoramic_dental_dataset', 'annotations', 'bboxes_caries')
    bboxes_teeth_dir = os.path.join(base_dir, 'panoramic_dental_dataset', 'annotations', 'bboxes_teeth')
    destino = os.path.join(base_dir, 'panoramic_dental_dataset', 'organizado')
    os.makedirs(destino, exist_ok=True)
    for clase in ['sano', 'patologico', 'sin_anotacion']:
        os.makedirs(os.path.join(destino, clase), exist_ok=True)
    for fname in os.listdir(images_dir):
        if not fname.lower().endswith('.png'):
            continue
        base = os.path.splitext(fname)[0]
        caries_path = os.path.join(bboxes_caries_dir, f'{base}.txt')
        teeth_path = os.path.join(bboxes_teeth_dir, f'{base}.txt')
        src = os.path.join(images_dir, fname)
        if os.path.exists(caries_path):
            # Si hay cajas de caries y el archivo no está vacío
            with open(caries_path) as f:
                contenido = f.read().strip()
            if contenido:
                shutil.copy2(src, os.path.join(destino, 'patologico', fname))
                continue
        if os.path.exists(teeth_path):
            # Si solo hay cajas de dientes (y no de caries)
            shutil.copy2(src, os.path.join(destino, 'sano', fname))
        else:
            shutil.copy2(src, os.path.join(destino, 'sin_anotacion', fname))
    print(f"Organización terminada en {destino}")

organizar_panoramic_dental_dataset(base_dir)

# (El resto del script sigue igual)
