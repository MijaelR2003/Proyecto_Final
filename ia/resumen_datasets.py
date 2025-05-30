import os

def contar_imagenes_en_carpetas(ruta_base):
    resumen = {}
    for root, dirs, files in os.walk(ruta_base):
        for d in dirs:
            dir_path = os.path.join(root, d)
            imagenes = [f for f in os.listdir(dir_path) if f.lower().endswith(('.jpg','.jpeg','.png'))]
            resumen[os.path.relpath(dir_path, ruta_base)] = len(imagenes)
    return resumen

def mostrar_resumen(nombre, ruta):
    print(f"\nResumen para {nombre}:")
    resumen = contar_imagenes_en_carpetas(ruta)
    for carpeta, cantidad in sorted(resumen.items()):
        print(f"  {carpeta}: {cantidad} imágenes")
    print(f"  TOTAL: {sum(resumen.values())} imágenes")

if __name__ == "__main__":
    base = os.path.dirname(__file__)
    mostrar_resumen('dental_radiography/train/organizado', os.path.join(base, 'dental_radiography', 'train', 'organizado'))
    mostrar_resumen('dental_radiography/test/organizado', os.path.join(base, 'dental_radiography', 'test', 'organizado'))
    mostrar_resumen('dental_radiography/valid/organizado', os.path.join(base, 'dental_radiography', 'valid', 'organizado'))
    mostrar_resumen('panoramic_dental_dataset/organizado', os.path.join(base, 'panoramic_dental_dataset', 'organizado'))
    mostrar_resumen('panoramic_dental_xray_dataset/imagenes_extraidas/sin_clasificar', os.path.join(base, 'panoramic_dental_xray_dataset', 'imagenes_extraidas', 'sin_clasificar'))
