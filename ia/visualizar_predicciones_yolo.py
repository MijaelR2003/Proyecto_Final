# Script para visualizar predicciones de caries con YOLOv8
# Puedes usarlo en Google Colab o localmente (requiere ultralytics y opencv)
   
from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
import os

# Configura la ruta a tu modelo entrenado y a las imágenes que quieres probar
MODEL_PATH = '/content/drive/MyDrive/yolo_caries_runs/yolov8n-caries/weights/best.pt'  # Cambia si es necesario
IMAGES_DIR = '/content/dataset/dataset_yolo/images/val'  # O pon la ruta a tus imágenes de prueba

# Carga el modelo
model = YOLO(MODEL_PATH)

# Lista de imágenes para probar
imagenes = [os.path.join(IMAGES_DIR, f) for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# Visualiza las primeras N imágenes con predicciones
N = 5
for img_path in imagenes[:N]:
    results = model(img_path)
    # results[0].plot() devuelve una imagen numpy con las cajas dibujadas
    img_pred = results[0].plot()
    plt.figure(figsize=(10,6))
    plt.imshow(cv2.cvtColor(img_pred, cv2.COLOR_BGR2RGB))
    plt.title(f'Predicciones: {os.path.basename(img_path)}')
    plt.axis('off')
    plt.show()

print('Visualización terminada. Si no ves cajas, el modelo no detectó caries.')
