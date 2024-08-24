from fastapi import FastAPI
from typing import Union

from openAI.client import OpenAIClient

app = FastAPI()

IMAGE_PROMPT = "En una imagen donde se muestra una mano con los dedos extendidos, ¿qué movimiento esperas que haga la mano? Si la mano se cierra, devuelve 1. Si la mano se abre, devuelve 0. Si es un movimiento de pinzas, devuelve 2."


@app.get("/")
def read_root():
    client = OpenAIClient(api_key="")
    response = client.process_image(IMAGE_PROMPT)
    print(response)
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/train-data")
def train_data(data: dict):
    return {"data": data}

