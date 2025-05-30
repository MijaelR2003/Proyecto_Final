import os
import tensorflow as tf
from PIL import Image
import io

def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def parse_tfrecord_fn(example):
    feature_description = {
        'image_raw': tf.io.FixedLenFeature([], tf.string),
        'height': tf.io.FixedLenFeature([], tf.int64),
        'width': tf.io.FixedLenFeature([], tf.int64)
    }
    return tf.io.parse_single_example(example, feature_description)

def save_images_from_tfrecord(tfrecord_path, output_dir):
    output_dir = os.path.join(output_dir, 'sin_clasificar')
    os.makedirs(output_dir, exist_ok=True)
    raw_dataset = tf.data.TFRecordDataset([tfrecord_path])
    for i, raw_record in enumerate(raw_dataset):
        example = parse_tfrecord_fn(raw_record)
        img_bytes = example['image_raw'].numpy()
        img = Image.open(io.BytesIO(img_bytes))
        img.save(os.path.join(output_dir, f"img_{i}.png"))
        print(f"Imagen {i} guardada en {output_dir}")

if __name__ == "__main__":
    tfrecord_path = os.path.join(os.path.dirname(__file__), 'panoramic_dental_xray_dataset', 'Dental_Xray3.tfrec')
    output_dir = os.path.join(os.path.dirname(__file__), 'panoramic_dental_xray_dataset', 'imagenes_extraidas')
    save_images_from_tfrecord(tfrecord_path, output_dir)
