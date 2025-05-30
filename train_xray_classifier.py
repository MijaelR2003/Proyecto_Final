import os
import tensorflow as tf
from tensorflow.keras.preprocessing import image_dataset_from_directory
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

# --- CONFIGURACIÓN ---
DATASET_DIR = 'dataset'  # Debe contener dental_xray/ y not_xray/
IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 10
MODEL_OUT = 'modelo_radiografia.h5'

# --- CARGA DE DATOS ---
train_ds = image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)
val_ds = image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

# Prefetch para rendimiento
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

# --- MODELO ---
base_model = MobileNetV2(input_shape=IMG_SIZE + (3,), include_top=False, weights='imagenet')
base_model.trainable = False  # Transfer learning

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dropout(0.2)(x)
pred = Dense(1, activation='sigmoid')(x)

model = Model(inputs=base_model.input, outputs=pred)
model.compile(optimizer=Adam(learning_rate=1e-4), loss='binary_crossentropy', metrics=['accuracy'])

# --- ENTRENAMIENTO ---
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS
)

# --- GUARDAR ---
model.save(MODEL_OUT)
print(f"Modelo guardado en {MODEL_OUT}")

# --- EVALUACIÓN FINAL ---
loss, acc = model.evaluate(val_ds)
print(f"Accuracy en validación: {acc:.4f}")

# --- USO ---
# Para predecir en Flask: cargar con tf.keras.models.load_model('modelo_radiografia.h5')
# y usar model.predict() sobre imágenes preprocesadas igual que aquí.
