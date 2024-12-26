import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
import ollama
from PIL import Image, ExifTags

load_dotenv()

MODEL_TYPE = "gemini"  
MODEL_NAME = "gemini-2.0-flash-exp"   
LOCAL_MODEL_NAME = "llama3.2-vision"  

PROMPT = (
    "Here is a thermal image from solar panels. "
    "They are purple rectangles. If there are orange spots inside the purple, "
    "that means the panel is damaged. If the panel is completely purple, it's fine. "
    "Only tell me True if damaged and False if not."
)

INPUT_IMAGES_DIR = "placas/test/"
TXT_OUTPUT_DIR    = "txt_outputs"

VALID_EXTENSIONS = (".jpeg", ".jpg", ".png")

REQUEST_DELAY = 2

RED    = "\033[91m"
GREEN  = "\033[92m"
BLUE   = "\033[94m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def get_decimal_from_dms(dms_tuple, ref):
    """
    Convierte (grados, minutos, segundos) a coordenadas decimales.
    Aplica signo negativo si la referencia es 'S' o 'W'.
    """
    degrees, minutes, seconds = dms_tuple
    decimal = degrees + minutes / 60.0 + seconds / 3600.0
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def get_gps_coordinates(exif_data):
    """
    Recibe un dict de metadatos EXIF y devuelve (lat, lon).
    """
    gps_info = exif_data.get('GPSInfo')
    if not gps_info:
        return None

    lat_dms = gps_info.get(2)  # (grados, minutos, segundos)
    lat_ref = gps_info.get(1)  # 'N' o 'S'
    lon_dms = gps_info.get(4)  # (grados, minutos, segundos)
    lon_ref = gps_info.get(3)  # 'E' o 'W'

    if lat_dms and lat_ref and lon_dms and lon_ref:
        lat = get_decimal_from_dms(lat_dms, lat_ref)
        lon = get_decimal_from_dms(lon_dms, lon_ref)
        return (lat, lon)
    return None

def get_image_metadata(image_path):
    """
    Retorna todos los metadatos EXIF en un dict o un string si no hay metadatos.
    """
    image = Image.open(image_path)
    exif_raw = image._getexif()
    if not exif_raw:
        return "No EXIF metadata found"

    exif_data = {}
    for tag, value in exif_raw.items():
        tag_name = ExifTags.TAGS.get(tag, tag)
        exif_data[tag_name] = value

    return exif_data

def get_image_coordinates(image_path):
    """
    Retorna (lat, lon) si la imagen tiene info GPS; None si no la tiene.
    """
    metadata = get_image_metadata(image_path)
    if isinstance(metadata, dict):
        return get_gps_coordinates(metadata)
    return None

class VisionModelBase:
    """
    Clase base para un modelo de visión. 
    Todos deben implementar .generate_response(prompt, image_path).
    """
    def generate_response(self, prompt, image_path):
        raise NotImplementedError("Esta es una clase base.")


class GeminiVision(VisionModelBase):
    """
    Visión con Google Gemini (API).
    """
    def __init__(self, model_name):
        self.model_name = model_name
        # Configurar la API Key
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def generate_response(self, prompt, image_path):
        # Abrir la imagen y pasarla al modelo
        img = Image.open(image_path)
        response = self.model.generate_content([prompt, img], stream=True)
        response.resolve()
        return response.text


class OllamaVision(VisionModelBase):
    """
    Visión con Ollama (modelo local LLaMA).
    """
    def __init__(self, model_name):
        self.model_name = model_name

    def generate_response(self, prompt, image_path):
        response = ollama.chat(
            model=self.model_name,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [image_path]
            }]
        )
        return response.message.content

def create_vision_model(model_type, gemini_name, ollama_name):
    """
    Devuelve una instancia de la clase que corresponda según model_type.
    """
    if model_type.lower() == "gemini":
        return GeminiVision(gemini_name)
    elif model_type.lower() == "ollama":
        return OllamaVision(ollama_name)
    else:
        raise ValueError(f"Tipo de modelo desconocido: {model_type}")

def imprimir_resultado(response_text, img_path):
    """
    Imprime el resultado según la respuesta del modelo 
    e incluye las coordenadas GPS (si existen).
    """
    if "true" in response_text.lower():
        coords = get_image_coordinates(img_path)
        print(f"{RED}{BOLD}La placa en {BLUE}{img_path}{RED} está dañada.{RESET}")
        if coords:
            lat, lon = coords
            print(f"  {BOLD}Coordenadas GPS encontradas:{RESET}")
            print(f"    Latitud : {lat}")
            print(f"    Longitud: {lon}")
        else:
            print("  No se encontraron coordenadas GPS.")
    else:
        print(f"{GREEN}{BOLD}La placa en {BLUE}{img_path}{GREEN} está en buen estado.{RESET}")

def process_images(input_dir, output_dir, model, prompt):
    """
    Recorre la carpeta, procesa cada imagen con el modelo,
    y guarda el resultado .txt en output_dir (opcional).
    """
    os.makedirs(output_dir, exist_ok=True)

    for root, dirs, files in os.walk(input_dir):
        for image_file in files:
            if image_file.lower().endswith(VALID_EXTENSIONS):

                image_path = os.path.join(root, image_file)
                response_text = model.generate_response(prompt, image_path)

                imprimir_resultado(response_text, image_path)

                relative_path = os.path.relpath(root, input_dir)
                output_subdir = os.path.join(output_dir, relative_path)
                os.makedirs(output_subdir, exist_ok=True)

                txt_filename = os.path.splitext(image_file)[0] + ".txt"
                txt_path = os.path.join(output_subdir, txt_filename)
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(response_text)

                time.sleep(REQUEST_DELAY)

if __name__ == "__main__":

    vision_model = create_vision_model(MODEL_TYPE, MODEL_NAME, LOCAL_MODEL_NAME)

    os.makedirs(TXT_OUTPUT_DIR, exist_ok=True)

    process_images(INPUT_IMAGES_DIR, TXT_OUTPUT_DIR, vision_model, PROMPT)
