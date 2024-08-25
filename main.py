from fastapi import FastAPI
from openAI.client import OpenAIClient
import requests
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes especificar el dominio del frontend en lugar de "*"
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los headers
)

IMAGE_PROMPT =f"""
Como una mano protésica con cinco dedos humanos, identificados como FINGERS = {{ 'index_finger': 'Dedo índice', 'middle_finger': 'Dedo medio', 'ring_finger': 'Dedo anular', 'pinky_finger': 'Dedo meñique', 'lower_thumb': 'Gordo bajo', 'upper_thumb': 'Gordo alto' }}, 
debes generar instrucciones de movimiento precisas para cada motor que controla un dedo. Los valores de movimiento de cada motor están comprendidos entre 0 (dedo completamente extendido) y 1 (dedo completamente cerrado). 
El 'lower_thumb' controla la posición del pulgar con respecto a la palma, mientras que el 'upper_thumb' controla la flexión del pulgar.
Tu tarea es analizar la imagen proporcionada y, 
basándote en los objetos o acciones visibles, generar un conjunto de comandos que describan cómo la mano protésica debe moverse para interactuar de manera óptima con el entorno. 
El formato de salida debe ser estrictamente una lista de diccionarios con la siguiente estructura:
[
    {{"engine": "upper_thumb", "value": 1}},
    {{"engine": "lower_thumb", "value": 0.8}},
    {{"engine": "index_finger", "value": 0.5}},
    {{"engine": "middle_finger", "value": 0}},
    {{"engine": "ring_finger", "value": 0}},
    {{"engine": "pinky_finger", "value": 0}}
]
Ten en cuenta las siguientes directrices clave:
1. **Secuencia de Movimiento:** Para abrir completamente la mano, comienza moviendo primero el pulgar ('upper_thumb' y 'lower_thumb') y luego los demás dedos. Al cerrar la mano, realiza el movimiento en orden inverso, empezando por los demás dedos y terminando con el pulgar. Asegúrate de que los movimientos sean suaves y naturales, siguiendo el orden correcto.
2. **Adaptación a Objetos:** Si en la imagen se identifica un objeto, ajusta los valores de los motores para que la mano lo agarre de manera precisa, manteniendo la conformidad de los dedos con la forma y tamaño del objeto. Evita cambios bruscos en los valores de los motores para asegurar un agarre seguro y estable.
3. **Justificación del Movimiento:** Para cada comando generado, considera la necesidad del movimiento en función del objeto o acción visible en la imagen. Justifica por qué el movimiento de cada motor es necesario y cómo contribuye a la interacción adecuada con el entorno. Esta justificación debe basarse en la forma, tamaño, y contexto del objeto, así como en la acción que se espera que la mano realice.
4. **Independencia de Movimientos:** Cada movimiento de motor debe ser independiente y determinado únicamente por la imagen proporcionada, sin considerar los movimientos anteriores. Esto asegura que cada comando sea preciso y específico para la situación actual.
Recuerda que no debes agregar información adicional fuera del formato especificado. El protocolo debe ser claro, preciso, y directamente aplicable a la imagen analizada.
"""

@app.get("/")
def ping():
    return {"response": "OK"}

class image(BaseModel):
    data: str

@app.post("/upload-image")
def upload_image(request: image):
    if request.data:
        client = OpenAIClient(api_key="")
        prompt = IMAGE_PROMPT
        image_data = request.data
        response = client.process_image2(prompt,image_data)
        cleaned_response = response.replace("```json", "").replace("```", "").strip()
        print(cleaned_response)
        post_data(cleaned_response)
        return {"response": cleaned_response}
    
def post_data(instructions):
    url = "http://10.67.10.73:8080/data"
    headers = {"Content-Type": "application/json"}

    payload = {"data": instructions}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("Data sent successfully")
        print(response.json())
    else:
        print("Error sending data")
        print(response.json())
