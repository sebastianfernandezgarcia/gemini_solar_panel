
# Solar Vision

## Descripción
**Solar Vision** es una herramienta diseñada para analizar imágenes térmicas de paneles solares y determinar su estado. Si detecta manchas naranjas en las áreas moradas de los paneles, identifica que están dañados. Además, puede extraer información GPS de las imágenes para localizar paneles defectuosos.

El sistema utiliza modelos de inteligencia artificial como **Google Gemini** y **Ollama (LLaMA)**, permitiendo flexibilidad entre modelos locales y en la nube.

---

## Requerimientos

Antes de comenzar, asegúrate de instalar las dependencias necesarias:

```bash
pip install google-generativeai Pillow python-dotenv ollama
```

---

## Estructura de Ficheros Recomendada

Asegúrate de organizar los archivos según la siguiente estructura:

```
├── solar_vision.py  # Archivo principal del proyecto
├── .env             # Archivo de configuración para la variable GOOGLE_API_KEY
├── input_images/    # Carpeta con las imágenes de entrada
│   ├── img1.jpg
│   └── img2.png
├── txt_outputs/     # Carpeta para guardar las salidas generadas
```

---

## Uso

Ejecuta el script principal desde la línea de comandos:

```bash
python solar_vision.py
```

El script:
1. Procesará todas las imágenes de la carpeta `input_images/`.
2. Analizará cada imagen utilizando el modelo seleccionado.
3. Imprimirá los resultados en la consola y guardará las respuestas en archivos `.txt` en la carpeta `txt_outputs/`.

---

## Configuración

### Variables de Entorno

Crea un archivo `.env` en el directorio principal para configurar la clave de la API de Google:

```
GOOGLE_API_KEY=tu_clave_de_api
```

### Selección del Modelo

Define el modelo que deseas usar en el código modificando la variable `MODEL_TYPE`. Las opciones disponibles son:
- `gemini`: Utiliza el modelo Google Gemini.
- `ollama`: Utiliza el modelo local LLaMA.

Ejemplo:
```python
MODEL_TYPE = "gemini"
```

---

## Características Principales

### 1. Detección de Daños en Paneles Solares
El script analiza las imágenes basándose en colores:
- **Morado**: Panel en buen estado.
- **Manchas Naranjas**: Panel dañado.

### 2. Extracción de Coordenadas GPS
Si las imágenes contienen metadatos EXIF con información GPS, el sistema extrae y muestra las coordenadas geográficas.

### 3. Salida Estructurada
Los resultados se imprimen en la consola y se guardan en archivos `.txt` organizados en subdirectorios dentro de `txt_outputs/`.

---

## Ejemplo de Salida

### Consola

```
La placa en img1.jpg está dañada.
  Coordenadas GPS encontradas:
    Latitud : 28.12345
    Longitud: -16.67890
```

### Archivo de Texto (`txt_outputs/img1.txt`)

```
True
La placa está dañada.
Coordenadas GPS:
- Latitud: 28.12345
- Longitud: -16.67890
```

---

## Notas

- **Retraso entre solicitudes:** Para evitar problemas con las APIs, el script incluye un retraso de 2 segundos entre el procesamiento de cada imagen.
- **Extensiones soportadas:** Las imágenes deben tener extensión `.jpeg`, `.jpg` o `.png`.

