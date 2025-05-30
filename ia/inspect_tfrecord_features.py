import os
import tensorflow as tf

def inspect_tfrecord(tfrecord_path, num_records=3):
    raw_dataset = tf.data.TFRecordDataset([tfrecord_path])
    for i, raw_record in enumerate(raw_dataset.take(num_records)):
        example = tf.train.Example()
        example.ParseFromString(raw_record.numpy())
        print(f"\nEjemplo {i}:")
        for key in example.features.feature:
            kind = example.features.feature[key].WhichOneof('kind')
            val = getattr(example.features.feature[key], kind)
            # Mostrar solo los primeros bytes si es muy largo
            if kind == 'bytes_list':
                print(f"  {key}: bytes_list (len={len(val.value)})")
            elif kind == 'float_list':
                print(f"  {key}: float_list (len={len(val.value)}) -> {val.value[:5]}")
            elif kind == 'int64_list':
                print(f"  {key}: int64_list (len={len(val.value)}) -> {val.value[:5]}")
            else:
                print(f"  {key}: {kind}")
        if i == num_records - 1:
            print("\n--- Fin de la inspección ---")

if __name__ == "__main__":
    tfrecord_path = os.path.join(os.path.dirname(__file__), 'panoramic_dental_xray_dataset', 'Dental_Xray3.tfrec')
    inspect_tfrecord(tfrecord_path)
