import os
from PIL import Image
import numpy as np

# Configuración
TAMANO = (224, 224)  # Puedes cambiar a 256,256 si prefieres
EXTENSIONES = ('.jpg', '.jpeg', '.png')

# Carpetas origen y destino (puedes agregar más si lo deseas)
CARPETAS = [
    ('dental_radiography/train/organizado', 'dental_radiography/train/preprocesado'),
    ('dental_radiography/test/organizado', 'dental_radiography/test/preprocesado'),
    ('dental_radiography/valid/organizado', 'dental_radiography/valid/preprocesado'),
    ('panoramic_dental_dataset/organizado', 'panoramic_dental_dataset/preprocesado'),
    ('panoramic_dental_xray_dataset/imagenes_extraidas/sin_clasificar', 'panoramic_dental_xray_dataset/imagenes_preprocesadas/sin_clasificar'),
]


def preprocesar_carpeta(origen, destino):
    origen_abs = os.path.join(os.path.dirname(__file__), origen)
    destino_abs = os.path.join(os.path.dirname(__file__), destino)
    for root, dirs, files in os.walk(origen_abs):
        rel = os.path.relpath(root, origen_abs)
        destino_dir = os.path.join(destino_abs, rel)
        os.makedirs(destino_dir, exist_ok=True)
        for f in files:
            if not f.lower().endswith(EXTENSIONES):
                continue
            ruta_img = os.path.join(root, f)
            try:
                img = Image.open(ruta_img).convert('RGB')
                img = img.resize(TAMANO)
                arr = np.array(img) / 255.0  # Normalización 0-1
                img_norm = Image.fromarray((arr * 255).astype(np.uint8))
                img_norm.save(os.path.join(destino_dir, f))
            except Exception as e:
                print(f"Error procesando {ruta_img}: {e}")

if __name__ == "__main__":
    for origen, destino in CARPETAS:
        print(f"Preprocesando {origen} -> {destino}")
        preprocesar_carpeta(origen, destino)
    print("Preprocesamiento terminado.")
