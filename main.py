from fastapi import FastAPI
from typing import Union
import httpx
from openAI.client import OpenAIClient
from rules.rules import CLOSE_HAND, OPEN_HAND, PINCH_GRIP
import requests

app = FastAPI()

IMAGE_PROMPT = f"""
    Analiza la imagen y determina la posición más adecuada de la mano con base en los siguientes criterios:
    - Si la mano está en una posición completamente cerrada o sosteniendo un objeto de manera firme con la mayoría de los dedos cerrados hacia la palma, devuelve CLOSE_HAND.
    - Si la mano está parcialmente cerrada, con el pulgar e índice en contacto formando una pinza o sosteniendo un objeto pequeño, devuelve PINCH_GRIP.
    - Si la mano está abierta o extendida, sin que los dedos se toquen entre sí o si sostiene un objeto de forma relajada, devuelve OPEN_HAND.
    Selecciona la respuesta que mejor se ajuste a la imagen.
    Devuelve solo la key.
"""
PREVIOUS_RULE = None

@app.get("/")
def read_root():
    client = OpenAIClient(api_key="")
    global PREVIOUS_RULE
    prompt = IMAGE_PROMPT
    response = client.process_image(prompt)

    pretify_response = response
    if response == PREVIOUS_RULE:
        alternative_responses = {
            "CLOSE_HAND": "OPEN_HAND",
            "OPEN_HAND": "PINCH_GRIP",
            "PINCH_GRIP": "OPEN_HAND"
        }
        pretify_response = alternative_responses[response]
    
    PREVIOUS_RULE = pretify_response

    returned_rules = {
        "CLOSE_HAND": CLOSE_HAND,
        "OPEN_HAND": OPEN_HAND,
        "PINCH_GRIP": PINCH_GRIP
    }
    rule = returned_rules[pretify_response]
    return {"response": rule}



@app.get("/test")
def train_data(data: dict):
    url = "http://10.67.10.73:8080/data"
    headers = {
        "Content-Type": "application/json",
    }
    data = [
        {"engine": "upper_thumb", "value": 1},
        {"engine": "lower_thumb", "value": 0.8},
        {"engine": "index_finger", "value": 0.50},
        {"engine": "middle_finger", "value": 0},
        {"engine": "ring_finger", "value": 0},
        {"engine": "pinky_finger", "value": 0},
    ]

    # Convertir la lista de diccionarios en una cadena JSON
    engine_status_list_json = {"engine_status_list_json": data}

    # Incluirla en los parámetros de la consulta en la URL
    # params = {
    #     "engine_status_list": engine_status_list_json
    # }

    response = requests.post(url, headers=headers, data=engine_status_list_json)
    # response = httpx.post(url, headers=headers, data=engine_status_list_json)
    return {"external_response": response.json()}


