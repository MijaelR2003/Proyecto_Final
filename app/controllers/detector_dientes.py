# app/controllers/detector_dientes.py
from ultralytics import YOLO
import cv2
import numpy as np
import os
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class TeethDetector:
    def __init__(self):
        # Ruta al modelo entrenado (ajustar según tu estructura)
        model_path = os.path.join(current_app.root_path, 'models', 'weights', 'best.pt')
        
        if not os.path.exists(model_path):
            logger.error(f"Modelo no encontrado en: {model_path}")
            raise FileNotFoundError(f"Modelo de dientes no encontrado: {model_path}")
        
        self.model = YOLO(model_path)
        logger.info(f"Modelo de detección de dientes cargado desde: {model_path}")
        
    def detectar_dientes(self, imagen_path, confidence=0.3):
        """
        Detecta dientes en una radiografía periapical
        
        Args:
            imagen_path: Ruta a la imagen
            confidence: Umbral de confianza (0.0-1.0)
            
        Returns:
            dict: Resultados de la detección
        """
        try:
            logger.info(f"Detectando dientes en: {imagen_path}")
            
            # Verificar que existe la imagen
            if not os.path.exists(imagen_path):
                return {
                    'success': False,
                    'error': f'Imagen no encontrada: {imagen_path}'
                }
            
            # Hacer predicción con YOLO
            results = self.model(imagen_path, conf=confidence)
            result = results[0]
            
            # Procesar resultados
            if result.masks is not None and len(result.masks.data) > 0:
                num_dientes = len(result.masks.data)
                confidences = result.boxes.conf.cpu().numpy()
                
                logger.info(f"Detectados {num_dientes} dientes con confianza promedio: {confidences.mean():.3f}")
                
                return {
                    'success': True,
                    'num_dientes': num_dientes,
                    'confidencias': confidences.tolist(),
                    'confianza_promedio': float(confidences.mean()),
                    'confianza_minima': float(confidences.min()),
                    'confianza_maxima': float(confidences.max()),
                    'detecciones_encontradas': True,
                    'resultado_yolo': result
                }
            else:
                logger.warning(f"No se detectaron dientes en: {imagen_path}")
                return {
                    'success': True,
                    'num_dientes': 0,
                    'detecciones_encontradas': False,
                    'mensaje': 'No se detectaron dientes en la imagen'
                }
                
        except Exception as e:
            logger.error(f"Error en detección de dientes: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Función auxiliar para usar en el controlador
def detectar_y_guardar(imagen_path, output_path, confidence=0.3):
    """
    Detecta dientes y guarda imagen con anotaciones
    
    Args:
        imagen_path: Ruta de imagen original
        output_path: Ruta donde guardar resultado
        confidence: Umbral de confianza
        
    Returns:
        tuple: (num_dientes, ruta_imagen_resultado)
    """
    try:
        detector = TeethDetector()
        resultado = detector.detectar_dientes(imagen_path, confidence)
        
        if not resultado['success']:
            logger.error(f"Error en detección: {resultado.get('error', 'Error desconocido')}")
            return 0, None
        
        if not resultado['detecciones_encontradas']:
            logger.warning("No se detectaron dientes")
            return 0, None
        
        # Crear imagen con anotaciones
        result_yolo = resultado['resultado_yolo']
        imagen_anotada = result_yolo.plot()
        
        # Guardar imagen resultado
        success = cv2.imwrite(output_path, imagen_anotada)
        
        if success:
            logger.info(f"Imagen con detecciones guardada en: {output_path}")
            return resultado['num_dientes'], output_path
        else:
            logger.error(f"No se pudo guardar imagen en: {output_path}")
            return resultado['num_dientes'], None
            
    except Exception as e:
        logger.error(f"Error en detectar_y_guardar: {str(e)}")
        return 0, None