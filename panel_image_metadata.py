from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_decimal_from_dms(dms, ref):
    """
    Convierte la tupla (grados, minutos, segundos) a coordenadas decimales.
    Aplica signo negativo si la referencia es 'S' o 'W'.
    """
    degrees, minutes, seconds = dms
    decimal = degrees + minutes / 60.0 + seconds / 3600.0
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def get_gps_coordinates(exif_data):
    """
    Devuelve una tupla (latitud, longitud) en decimal a partir de la sección GPSInfo.
    Si no encuentra GPSInfo, devuelve None.
    """
    gps_info = exif_data.get('GPSInfo', {})
    if not gps_info:
        return None
    
    # Claves más comunes en GPSInfo
    lat_dms = gps_info.get(2)  # (grados, minutos, segundos)
    lat_ref = gps_info.get(1)  # 'N' o 'S'
    lon_dms = gps_info.get(4)  # (grados, minutos, segundos)
    lon_ref = gps_info.get(3)  # 'E' o 'W'
    
    if lat_dms and lat_ref and lon_dms and lon_ref:
        lat = get_decimal_from_dms(lat_dms, lat_ref)
        lon = get_decimal_from_dms(lon_dms, lon_ref)
        return (lat, lon)
    else:
        return None

def get_image_metadata(image_path):
    """
    Devuelve todos los metadatos EXIF en un diccionario,
    o un string si no se encuentra información.
    """
    image = Image.open(image_path)
    exif_data = image._getexif()
    
    if exif_data is not None:
        metadata = {}
        for tag, value in exif_data.items():
            # Usamos TAGS para traducir la etiqueta numérica a su nombre
            tag_name = TAGS.get(tag, tag)
            metadata[tag_name] = value
        return metadata
    else:
        return "No EXIF metadata found"

def mis_coordenadas(image_path):
    # Cambia esta ruta a tu imagen
    
    
    # 1. Obtenemos todos los metadatos
    metadata = get_image_metadata(image_path)
    
    # 2. Si metadata es un diccionario, imprimimos todo y luego extraemos GPS
    if isinstance(metadata, dict):
        #print("---- Metadatos EXIF ----")
        #for key, value in metadata.items():
            #print(f"{key}: {value}")
        
        # 3. Extraemos las coordenadas GPS
        gps_coords = get_gps_coordinates(metadata)
        return gps_coords
        """
        if gps_coords:
            lat, lon = gps_coords
            print("\nEn la siguientes Coordenadas GPS:")
            print(f"Latitud: {lat}")
            print(f"Longitud: {lon}")
        else:
            print("\nNo se encontró información GPS en la imagen.")
        """
    else:
        return metadata
        print(metadata)

if __name__ == "__main__":

    metadata = get_image_metadata(image_path = 'test/DJI_20240711113846_0317_T_D.JPG')
    if isinstance(metadata, dict):
        print("---- Metadatos EXIF ----")
        for key, value in metadata.items():
            print(f"{key}: {value}")