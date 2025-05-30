import os
import matplotlib.pyplot as plt
import tensorflow as tf

# Configuración
IMG_SIZE = (224, 224)
BATCH_SIZE = 32

# Paths
base_dir = os.path.dirname(__file__)
train_dir = os.path.join(base_dir, 'dental_radiography', 'train', 'preprocesado')
valid_dir = os.path.join(base_dir, 'dental_radiography', 'valid', 'preprocesado')
test_dir = os.path.join(base_dir, 'dental_radiography', 'test', 'preprocesado')

# Cargar datasets
train_ds = tf.keras.utils.image_dataset_from_directory(
    train_dir,
    labels='inferred',
    label_mode='categorical',
    batch_size=BATCH_SIZE,
    image_size=IMG_SIZE,
    shuffle=True,
    seed=42
)
valid_ds = tf.keras.utils.image_dataset_from_directory(
    valid_dir,
    labels='inferred',
    label_mode='categorical',
    batch_size=BATCH_SIZE,
    image_size=IMG_SIZE,
    shuffle=False
)
test_ds = tf.keras.utils.image_dataset_from_directory(
    test_dir,
    labels='inferred',
    label_mode='categorical',
    batch_size=BATCH_SIZE,
    image_size=IMG_SIZE,
    shuffle=False
)

# Mostrar distribución de clases
class_names = train_ds.class_names
print("Clases:", class_names)

from collections import Counter
all_labels = []
for images, labels in train_ds.unbatch():
    all_labels.append(tf.argmax(labels).numpy())
print("Distribución de clases en train:", Counter(all_labels))

# Mostrar ejemplos aleatorios
plt.figure(figsize=(10, 6))
for images, labels in train_ds.take(1):
    for i in range(9):
        ax = plt.subplot(3, 3, i + 1)
        plt.imshow(images[i].numpy().astype("uint8"))
        idx = tf.argmax(labels[i]).numpy()
        plt.title(class_names[idx])
        plt.axis("off")
plt.tight_layout()
plt.show()
