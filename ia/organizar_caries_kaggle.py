import os
import shutil

# Directorios
base_dir = os.path.join(os.path.dirname(__file__), 'adult_caries_detection', 'Adult Dataset Caries Detection')
images_dir = os.path.join(base_dir, 'images')
labels_dir = os.path.join(base_dir, 'caries_labels')
output_dir = os.path.join(os.path.dirname(__file__), 'datasets', 'caries_kaggle_clasificacion')

os.makedirs(os.path.join(output_dir, 'caries'), exist_ok=True)
os.makedirs(os.path.join(output_dir, 'no_caries'), exist_ok=True)

def organizar():
    # Clasifica como 'caries' si existe un archivo de etiqueta para la imagen, 'no_caries' si no existe
    for img_file in os.listdir(images_dir):
        if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
            img_id = os.path.splitext(img_file)[0]
            label_file = os.path.join(labels_dir, f'{img_id}.txt')
            if os.path.exists(label_file):
                destino = os.path.join(output_dir, 'caries', img_file)
            else:
                destino = os.path.join(output_dir, 'no_caries', img_file)
            shutil.copy2(os.path.join(images_dir, img_file), destino)
    print('¡Imágenes organizadas para clasificación binaria en:', output_dir)

if __name__ == '__main__':
    organizar()
