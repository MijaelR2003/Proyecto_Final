import os
import random
import pandas as pd
import numpy as np
import shutil

# Parámetros
N_CLASES = 2  # 0: no endodoncia, 1: requiere endodoncia
N_SAMPLES_POR_CLASE = 20  # Puedes aumentar para más datos
IMG_SIZE = (224, 224)

# Columnas clínicas
clin_vars = [
    'dolor_persistente','sensibilidad_prolongada','hinchazon','fistula','cambio_color',
    'dolor_percusion','movilidad','caries_profunda','lesion_radiografica'
]

# Carpeta de imágenes base (elige imágenes reales para copiar)
img_base_dir = os.path.join(os.path.dirname(__file__), 'datasets', 'caries_kaggle_clasificacion')
img_caries = [os.path.join(img_base_dir, 'caries', f) for f in os.listdir(os.path.join(img_base_dir, 'caries')) if f.endswith(('.jpg','.png','.jpeg'))]
img_no_caries = [os.path.join(img_base_dir, 'no_caries', f) for f in os.listdir(os.path.join(img_base_dir, 'no_caries')) if f.endswith(('.jpg','.png','.jpeg'))]

# Carpeta para imágenes sintéticas
synth_img_dir = os.path.join(os.path.dirname(__file__), 'media', 'synth')
os.makedirs(synth_img_dir, exist_ok=True)

rows = []
paciente_id = 100
revision_id = 200
imagen_id = 1000

for clase in range(N_CLASES):
    for i in range(N_SAMPLES_POR_CLASE):
        # Generar datos clínicos aleatorios variados
        clinicos = [random.randint(0,1) for _ in clin_vars]
        # Asegurar que la clase tenga sentido clínico
        if clase == 1:
            clinicos[-1] = 1  # lesion_radiografica=1 para endodoncia
        else:
            clinicos[-1] = 0  # lesion_radiografica=0 para no endodoncia
        # Seleccionar y copiar una imagen real de la clase correspondiente
        if clase == 1:
            img_src = random.choice(img_caries)
        else:
            img_src = random.choice(img_no_caries)
        img_dst_name = f'synth_{clase}_{i}.jpg'
        img_dst_path = os.path.join(synth_img_dir, img_dst_name)
        shutil.copy2(img_src, img_dst_path)
        # Crear fila
        row = {
            'paciente_id': paciente_id,
            'revision_id': revision_id,
            'imagen_id': imagen_id,
            'imagen_path': img_dst_path,
        }
        row.update({k: v for k, v in zip(clin_vars, clinicos)})
        row['diagnostico_endodoncia'] = clase
        rows.append(row)
        paciente_id += 1
        revision_id += 1
        imagen_id += 1

# Guardar en CSV
csv_path = os.path.join(os.path.dirname(__file__), 'dataset_clinico_multimodal.csv')
df = pd.DataFrame(rows)
df.to_csv(csv_path, index=False)
print(f'Datos sintéticos generados y guardados en {csv_path}')
