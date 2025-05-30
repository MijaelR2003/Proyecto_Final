#!/bin/bash
# Descarga los 3 datasets principales de radiografías dentales de Kaggle
# Requiere tener configurado kaggle.json correctamente

set -e

# Dataset 1: Dental Radiography
kaggle datasets download -d mohammadrezamomeni/dental-radiography -p dental_radiography --unzip

# Dataset 2: Panoramic Dental Dataset
kaggle datasets download -d thunderpede/panoramic-dental-dataset -p panoramic_dental_dataset --unzip

# Dataset 3: Panoramic Dental Xray Dataset
kaggle datasets download -d daverattan/panoramic-dental-xray-dataset -p panoramic_dental_xray_dataset --unzip

echo "¡Todos los datasets descargados y extraídos!"
