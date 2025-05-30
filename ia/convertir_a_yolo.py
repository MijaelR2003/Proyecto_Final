import os
import shutil
import random

# Configuración
RUTA_DATASET = os.path.join(os.path.dirname(__file__), 'panoramic_dental_dataset')
IMAGES_DIR = os.path.join(RUTA_DATASET, 'images')
BBOXES_DIR = os.path.join(RUTA_DATASET, 'annotations', 'bboxes_caries')

DESTINO = os.path.join(os.path.dirname(__file__), 'dataset_yolo')
IMGS_OUT = os.path.join(DESTINO, 'images')
LBL_OUT = os.path.join(DESTINO, 'labels')

SPLIT_TRAIN = 0.8  # 80% train, 20% val

# Crear estructura
for split in ['train', 'val']:
    os.makedirs(os.path.join(IMGS_OUT, split), exist_ok=True)
    os.makedirs(os.path.join(LBL_OUT, split), exist_ok=True)

# Listar imágenes disponibles con bboxes
imagenes = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith('.png')]
random.shuffle(imagenes)
n_train = int(len(imagenes) * SPLIT_TRAIN)
train_imgs = imagenes[:n_train]
val_imgs = imagenes[n_train:]
splits = [('train', train_imgs), ('val', val_imgs)]

def convertir_bbox_a_yolo(linea, ancho, alto):
    x1, y1, x2, y2 = map(float, linea.strip().split())
    x_center = ((x1 + x2) / 2) / ancho
    y_center = ((y1 + y2) / 2) / alto
    w = abs(x2 - x1) / ancho
    h = abs(y2 - y1) / alto
    return f"0 {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}"

for split, imgs in splits:
    for fname in imgs:
        img_path = os.path.join(IMAGES_DIR, fname)
        bbox_path = os.path.join(BBOXES_DIR, fname.replace('.png', '.txt'))
        # Copiar imagen
        out_img = os.path.join(IMGS_OUT, split, fname)
        shutil.copy2(img_path, out_img)
        # Leer tamaño imagen
        from PIL import Image
        with Image.open(img_path) as im:
            ancho, alto = im.size
        # Convertir bboxes
        yolo_lines = []
        if os.path.exists(bbox_path):
            with open(bbox_path) as f:
                for linea in f:
                    if linea.strip():
                        yolo_lines.append(convertir_bbox_a_yolo(linea, ancho, alto))
        # Guardar archivo YOLO
        out_lbl = os.path.join(LBL_OUT, split, fname.replace('.png', '.txt'))
        with open(out_lbl, 'w') as f:
            f.write('\n'.join(yolo_lines))
print('Conversión a formato YOLO terminada. Carpeta lista: dataset_yolo/')
