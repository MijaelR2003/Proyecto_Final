import os
import random
import matplotlib.pyplot as plt
from PIL import Image

def mostrar_ejemplos(base_dir, clases=['caries', 'no_caries'], n=5):
    """Muestra ejemplos aleatorios de cada clase"""
    fig, axs = plt.subplots(len(clases), n, figsize=(3*n, 3*len(clases)))
    for i, clase in enumerate(clases):
        clase_dir = os.path.join(base_dir, clase)
        imagenes = [f for f in os.listdir(clase_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        muestras = random.sample(imagenes, min(n, len(imagenes)))
        for j, img_file in enumerate(muestras):
            img_path = os.path.join(clase_dir, img_file)
            img = Image.open(img_path)
            axs[i, j].imshow(img, cmap='gray')
            axs[i, j].axis('off')
            axs[i, j].set_title(f'{clase}\n{img_file}')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    base_dir = os.path.join(os.path.dirname(__file__), 'datasets', 'caries_kaggle_clasificacion')
    mostrar_ejemplos(base_dir)
