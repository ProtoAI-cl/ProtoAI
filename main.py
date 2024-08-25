from fastapi import FastAPI
from openAI.client import OpenAIClient
import requests
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from promts.promts import HAND_PROMT, HAND_PROMT_2, HAND_PROMT_3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

IMAGE_PROMPT = HAND_PROMT_3

@app.get("/")
def ping():
    return {"response": "OK"}

class image(BaseModel):
    data: str

@app.post("/upload-image")
def upload_image(request: image):
    # api_key = os.getenv("OPENAI_API_KEY")
    # if not api_key:
    #     return {"error": "API key not found"}
    
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
