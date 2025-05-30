import os
import pandas as pd
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras import layers, models, Input, Model
from sklearn.model_selection import train_test_split

# Parámetros
IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 15

# Cargar dataset
csv_path = os.path.join(os.path.dirname(__file__), 'dataset_clinico_multimodal.csv')
# Leer el CSV y limpiar filas no válidas
raw_df = pd.read_csv(csv_path, comment='#')
# Eliminar filas que no sean datos (cabeceras repetidas, filas de ejemplo)
df = raw_df.copy()
df = df[df['paciente_id'].apply(lambda x: str(x).isdigit())]
df = df[df['diagnostico_endodoncia'].apply(lambda x: str(x).isdigit())]
df = df.reset_index(drop=True)

# Columnas clínicas
clin_vars = [
    'dolor_persistente','sensibilidad_prolongada','hinchazon','fistula','cambio_color',
    'dolor_percusion','movilidad','caries_profunda','lesion_radiografica'
]

# Procesar rutas de imagen y etiquetas
img_paths = df['imagen_path'].astype(str).tolist()
img_paths = [os.path.join(os.path.dirname(__file__), path) if not os.path.isabs(path) else path for path in img_paths]
X_imgs = img_paths
X_clin = df[clin_vars].astype(np.float32).values
y = df['diagnostico_endodoncia'].astype(np.float32).values

# Split train/val
X_imgs_train, X_imgs_val, X_clin_train, X_clin_val, y_train, y_val = train_test_split(
    X_imgs, X_clin, y, test_size=0.2, random_state=42, stratify=y
)

def load_image(path):
    img = Image.open(path).convert('RGB').resize(IMG_SIZE)
    return np.array(img) / 255.0

def data_generator(img_paths, clin_vars, labels, batch_size):
    idxs = np.arange(len(img_paths))
    while True:
        np.random.shuffle(idxs)
        for i in range(0, len(img_paths), batch_size):
            batch_idxs = idxs[i:i+batch_size]
            batch_imgs = np.array([load_image(img_paths[j]) for j in batch_idxs])
            batch_clin = clin_vars[batch_idxs]
            batch_labels = labels[batch_idxs]
            yield [batch_imgs, batch_clin], batch_labels

# Modelos
# Rama imagen
img_input = Input(shape=(*IMG_SIZE, 3), name='img_input')
x = layers.Conv2D(32, (3,3), activation='relu')(img_input)
x = layers.MaxPooling2D(2,2)(x)
x = layers.Conv2D(64, (3,3), activation='relu')(x)
x = layers.MaxPooling2D(2,2)(x)
x = layers.Conv2D(128, (3,3), activation='relu')(x)
x = layers.MaxPooling2D(2,2)(x)
x = layers.Flatten()(x)
x = layers.Dense(128, activation='relu')(x)
x = layers.Dropout(0.3)(x)

# Rama clínica
clin_input = Input(shape=(len(clin_vars),), name='clin_input')
yc = layers.Dense(32, activation='relu')(clin_input)
yc = layers.Dense(16, activation='relu')(yc)

# Concatenación
concat = layers.concatenate([x, yc])
out = layers.Dense(1, activation='sigmoid')(concat)

model = Model(inputs=[img_input, clin_input], outputs=out)
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Generadores
train_gen = data_generator(X_imgs_train, X_clin_train, y_train, BATCH_SIZE)
val_gen = data_generator(X_imgs_val, X_clin_val, y_val, BATCH_SIZE)

steps_train = int(np.ceil(len(X_imgs_train)/BATCH_SIZE))
steps_val = int(np.ceil(len(X_imgs_val)/BATCH_SIZE))

# Entrenamiento
history = model.fit(
    train_gen,
    steps_per_epoch=steps_train,
    epochs=EPOCHS,
    validation_data=val_gen,
    validation_steps=steps_val
)

model.save(os.path.join(os.path.dirname(__file__), 'modelo_multimodal_endodoncia.h5'))
print('Entrenamiento terminado. Modelo guardado como modelo_multimodal_endodoncia.h5')
