import os
import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt

# Configuración
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 15
PATIENCE = 4

base_dir = os.path.dirname(__file__)
train_dir = os.path.join(base_dir, 'dental_radiography', 'train', 'preprocesado')
valid_dir = os.path.join(base_dir, 'dental_radiography', 'valid', 'preprocesado')
test_dir = os.path.join(base_dir, 'dental_radiography', 'test', 'preprocesado')

# Cargar datasets
train_ds = tf.keras.utils.image_dataset_from_directory(
    train_dir, labels='inferred', label_mode='categorical', batch_size=BATCH_SIZE,
    image_size=IMG_SIZE, shuffle=True, seed=42)
valid_ds = tf.keras.utils.image_dataset_from_directory(
    valid_dir, labels='inferred', label_mode='categorical', batch_size=BATCH_SIZE,
    image_size=IMG_SIZE, shuffle=False)
test_ds = tf.keras.utils.image_dataset_from_directory(
    test_dir, labels='inferred', label_mode='categorical', batch_size=BATCH_SIZE,
    image_size=IMG_SIZE, shuffle=False)

class_names = train_ds.class_names
num_classes = len(class_names)

# Data pipeline performance
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
valid_ds = valid_ds.prefetch(buffer_size=AUTOTUNE)
test_ds = test_ds.prefetch(buffer_size=AUTOTUNE)

# Modelo base MobileNetV2
base_model = tf.keras.applications.MobileNetV2(input_shape=IMG_SIZE+(3,), include_top=False, weights='imagenet')
base_model.trainable = False  # Fine-tune después de unas epochs si se desea

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.3),
    layers.Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Callbacks
checkpoint = tf.keras.callbacks.ModelCheckpoint(
    'mejor_modelo_dental.keras', monitor='val_accuracy', save_best_only=True, verbose=1)
early = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=PATIENCE, restore_best_weights=True)

# Entrenamiento
history = model.fit(
    train_ds,
    validation_data=valid_ds,
    epochs=EPOCHS,
    callbacks=[checkpoint, early]
)

# Gráficas de entrenamiento
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.plot(history.history['accuracy'], label='train_acc')
plt.plot(history.history['val_accuracy'], label='val_acc')
plt.title('Accuracy')
plt.legend()
plt.subplot(1,2,2)
plt.plot(history.history['loss'], label='train_loss')
plt.plot(history.history['val_loss'], label='val_loss')
plt.title('Loss')
plt.legend()
plt.tight_layout()
plt.savefig('entrenamiento_dental.png')
plt.close()

# Evaluación en test
modelo_final = tf.keras.models.load_model('mejor_modelo_dental.keras')
loss, acc = modelo_final.evaluate(test_ds, verbose=2)
print(f"\nTest accuracy: {acc:.4f}")
