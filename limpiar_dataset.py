import os
from PIL import Image

def limpiar_carpeta(carpeta):
    extensiones = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    eliminados = 0
    corruptos = 0
    total = 0
    for root, dirs, files in os.walk(carpeta):
        for file in files:
            ruta = os.path.join(root, file)
            total += 1
            # Eliminar si no es imagen
            if not file.lower().endswith(extensiones):
                print(f"Eliminando archivo no imagen: {ruta}")
                os.remove(ruta)
                eliminados += 1
            else:
                # Intentar abrir la imagen para verificar si está corrupta
                try:
                    with Image.open(ruta) as img:
                        img.verify()
                except Exception as e:
                    print(f"Eliminando imagen corrupta: {ruta} ({e})")
                    os.remove(ruta)
                    corruptos += 1
    print(f"En '{carpeta}': {eliminados} archivos no imagen eliminados, {corruptos} imágenes corruptas eliminadas, {total} archivos revisados.")

limpiar_carpeta('dataset/dental_xray')
limpiar_carpeta('dataset/not_xray')
print("¡Limpieza terminada!")
