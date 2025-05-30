import os
import zipfile
import requests

DATASET_DIR = os.path.join(os.path.dirname(__file__), 'dataset', 'not_xray')
ZIP_URL = 'https://github.com/EliSchwartz/imagenet-sample-images/archive/refs/heads/master.zip'
TEMP_ZIP = 'imagenet_samples.zip'

os.makedirs(DATASET_DIR, exist_ok=True)

print('Descargando imágenes de ejemplo de ImageNet...')
response = requests.get(ZIP_URL)
with open(TEMP_ZIP, 'wb') as f:
    f.write(response.content)

print('Extrayendo imágenes...')
with zipfile.ZipFile(TEMP_ZIP, 'r') as zip_ref:
    # Extraer solo archivos .JPEG de la carpeta imagenet-sample-images-master/n01440764/ etc.
    for file in zip_ref.namelist():
        if file.endswith('.JPEG'):
            # Extrae la imagen a la carpeta not_xray
            filename = os.path.basename(file)
            target_path = os.path.join(DATASET_DIR, filename)
            with zip_ref.open(file) as source, open(target_path, 'wb') as target:
                target.write(source.read())
print('Limpieza del zip...')
os.remove(TEMP_ZIP)
print(f'¡Listo! Imágenes descargadas en {DATASET_DIR}')
