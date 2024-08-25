from fastapi import FastAPI
from openAI.client import OpenAIClient
from rules.rules import CLOSE_HAND, OPEN_HAND, PINCH_GRIP


app = FastAPI()

IMAGE_PROMPT =f"""
Como una mano protésica con cinco dedos humanos, identificados como FINGERS = {{ 'index_finger': 'Dedo índice', 'middle_finger': 'Dedo medio', 'ring_finger': 'Dedo anular', 'pinky_finger': 'Dedo meñique', 'lower_thumb': 'Gordo bajo', 'upper_thumb': 'Gordo alto' }}, 
debes generar instrucciones de movimiento precisas para cada motor que controla un dedo. Los valores de movimiento de cada motor están comprendidos entre 0 (dedo completamente extendido) y 1 (dedo completamente cerrado). 
El 'lower_thumb' controla la posición del pulgar con respecto a la palma, mientras que el 'upper_thumb' controla la flexión del pulgar.
Tu tarea es analizar la imagen proporcionada y, 
basándote en los objetos o acciones visibles, generar un conjunto de comandos que describan cómo la mano protésica debe moverse para interactuar de manera óptima con el entorno. 
El formato de salida debe ser estrictamente una lista de diccionarios en JSON con la siguiente estructura:
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

PREVIOUS_RULE = None

@app.get("/")
def read_root():
    client = OpenAIClient(api_key="")
    global PREVIOUS_RULE
    prompt = IMAGE_PROMPT
    response = client.process_image(prompt)
    print(response)

    # pretify_response = response
    # if response == PREVIOUS_RULE:
    #     alternative_responses = {
    #         "CLOSE_HAND": "OPEN_HAND",
    #         "OPEN_HAND": "PINCH_GRIP",
    #         "PINCH_GRIP": "OPEN_HAND"
    #     }
    #     pretify_response = alternative_responses[response]
    
    # PREVIOUS_RULE = pretify_response

    # returned_rules = {
    #     "CLOSE_HAND": CLOSE_HAND,
    #     "OPEN_HAND": OPEN_HAND,
    #     "PINCH_GRIP": PINCH_GRIP
    # }
    # rule = returned_rules[pretify_response]
    return {"response": response}



# @app.get("/test")
# def train_data(data: dict):
#     url = "http://10.67.10.73:8080/data"
#     headers = {
#         "Content-Type": "application/json",
#     }
#     data = [
#         {"engine": "upper_thumb", "value": 1},
#         {"engine": "lower_thumb", "value": 0.8},
#         {"engine": "index_finger", "value": 0.50},
#         {"engine": "middle_finger", "value": 0},
#         {"engine": "ring_finger", "value": 0},
#         {"engine": "pinky_finger", "value": 0},
#     ]

#     # Convertir la lista de diccionarios en una cadena JSON
#     engine_status_list_json = {"engine_status_list_json": data}

#     # Incluirla en los parámetros de la consulta en la URL
#     # params = {
#     #     "engine_status_list": engine_status_list_json
#     # }

#     response = requests.post(url, headers=headers, data=engine_status_list_json)
#     # response = httpx.post(url, headers=headers, data=engine_status_list_json)
#     return {"external_response": response.json()}


