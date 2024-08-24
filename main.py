from fastapi import FastAPI
from typing import Union

from openAI.client import OpenAIClient
from rules.rules import CLOSE_HAND, OPEN_HAND, PINCH_GRIP

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


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/train-data")
def train_data(data: dict):
    return {"data": data}

