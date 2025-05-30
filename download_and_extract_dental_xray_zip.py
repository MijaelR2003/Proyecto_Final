import os
import requests
import zipfile

DATASET_DIR = os.path.join(os.path.dirname(__file__), 'dataset', 'dental_xray')
ZIP_URL = 'https://prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com/73n3kz2k4k-3.zip'
TEMP_ZIP = 'dental_xray_dataset.zip'

os.makedirs(DATASET_DIR, exist_ok=True)

print('Descargando dataset de radiografías dentales...')
response = requests.get(ZIP_URL, stream=True)
with open(TEMP_ZIP, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)

print('Extrayendo imágenes...')
with zipfile.ZipFile(TEMP_ZIP, 'r') as zip_ref:
    zip_ref.extractall(DATASET_DIR)

print('Limpieza del zip...')
os.remove(TEMP_ZIP)

# Contador de imágenes
count = 0
for root, dirs, files in os.walk(DATASET_DIR):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            count += 1
print(f'¡Listo! Imágenes extraídas en {DATASET_DIR}')
print(f'Total de imágenes en la carpeta: {count}')
