"""
Detector de dientes con modelo YOLO para uso en Flask
Adaptado del script Colab original que funciona para el usuario
"""
import os
import sys
import logging
import numpy as np
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

def procesar_imagen(imagen_path, output_path):
    """
    Procesa una imagen de rayos X dental usando el modelo YOLO pre-entrenado
    y guarda la imagen con las detecciones marcadas
    """
    try:
        # Importar aquí para evitar errores de inicialización si hay problemas
        logger.info("🔧 Configurando entorno e importando librerías...")
        from ultralytics import YOLO
        import cv2
        import torch
        
        # Verificar GPU (opcional, pero útil para diagnóstico)
        gpu_disponible = torch.cuda.is_available()
        logger.info(f"GPU disponible: {gpu_disponible}")
        if gpu_disponible:
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        
        # Imprimir rutas absolutas
        imagen_abs = os.path.abspath(imagen_path)
        output_abs = os.path.abspath(output_path)
        
        logger.info(f"Imagen a procesar: {imagen_abs}")
        logger.info(f"Ruta de salida: {output_abs}")
        
        # Verificar que la imagen existe
        if not os.path.exists(imagen_abs):
            logger.error(f"❌ ARCHIVO NO ENCONTRADO: {imagen_abs}")
            return 0, None
        
        # Verificar/crear directorio de salida
        os.makedirs(os.path.dirname(output_abs), exist_ok=True)
        
        # Buscar el modelo en varias ubicaciones posibles
        logger.info("🏋️‍♀️ Buscando modelo entrenado...")
        posibles_ubicaciones = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'modelo_dientes', 'modelo_dientes', 'weights', 'best.pt')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'modelo_dientes', 'weights', 'best.pt')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'modelo_dientes', 'best.pt'))
        ]
        
        modelo_path = None
        for ubicacion in posibles_ubicaciones:
            logger.info(f"Buscando en: {ubicacion}")
            if os.path.exists(ubicacion):
                modelo_path = ubicacion
                logger.info(f"✅ Modelo encontrado en: {modelo_path}")
                break
        
        if modelo_path is None:
            logger.error("❌ ERROR: MODELO NO ENCONTRADO EN NINGUNA UBICACIÓN")
            return 0, None
        
        # Cargar el modelo
        logger.info("Cargando modelo YOLO...")
        model = YOLO(modelo_path)
        logger.info("✅ Modelo cargado correctamente")
        
        # Ejecutar inferencia con confianza 0.3 como en el ejemplo de Colab
        logger.info(f"🚀 Ejecutando detección en '{os.path.basename(imagen_abs)}'...")
        results = model(imagen_abs, conf=0.3)
        result = results[0]  # primer resultado
        
        # Contar detecciones y calcular confianza promedio (como en el script de Colab)
        logger.info("📊 RESULTADOS DE LA PREDICCIÓN:")
        
        if result.masks is not None and hasattr(result.masks, 'data') and len(result.masks.data) > 0:
            # Modelo de segmentación con máscaras
            num_dientes = len(result.masks.data)
            confianzas = result.boxes.conf.cpu().numpy()
            conf_promedio = float(confianzas.mean())
            
            logger.info(f"   - Dientes detectados: {num_dientes}")
            logger.info(f"   - Confianza promedio: {conf_promedio:.3f}")
            
        elif result.boxes is not None and len(result.boxes) > 0:
            # Modelo de detección con cajas
            num_dientes = len(result.boxes)
            confianzas = result.boxes.conf.cpu().numpy()
            conf_promedio = float(confianzas.mean())
            
            logger.info(f"   - Dientes detectados: {num_dientes}")
            logger.info(f"   - Confianza promedio: {conf_promedio:.3f}")
            
        else:
            # No se detectaron dientes
            num_dientes = 0
            logger.info("   - ⚠️ No se detectaron dientes en la imagen.")
        
        # Generar y guardar visualización
        logger.info("👀 Generando imagen con detecciones...")
        img_anotada = result.plot()
        logger.info(f"Guardando resultado en: {output_abs}")
        cv2.imwrite(output_abs, img_anotada)
        
        return num_dientes, output_abs
        
    except Exception as e:
        logger.exception(f"❌ Error al procesar la imagen: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 0, None

# Para pruebas independientes
if __name__ == "__main__":
    if len(sys.argv) > 2:
        img_path = sys.argv[1]
        out_path = sys.argv[2]
        print(f"Probando con imagen: {img_path}")
        num, path = procesar_imagen(img_path, out_path)
        print(f"Resultado: {num} dientes detectados, guardado en {path}")
    else:
        print("Uso: python detector_simple.py imagen.jpg salida.jpg")
