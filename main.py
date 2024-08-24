from fastapi import FastAPI
from typing import Union

from openAI.client import OpenAIClient

app = FastAPI()



@app.get("/")
def read_root():
    client = OpenAIClient(api_key="")
    prompt = "Describe cómo funciona el modo pinza en una mano robótica."
    response = client.create_completion(prompt)
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/train-data")
def train_data(data: dict):
    return {"data": data}

