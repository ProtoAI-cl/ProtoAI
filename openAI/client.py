import openai
import openai.resources

from utils.images import encode_image

class OpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key


    def create_completion(self, prompt, model="gpt-4o-mini", max_tokens=50):
        chat_completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        message_content = chat_completion.choices[0].message.content
        return message_content
    
    def process_image(self):
        image_path = './images/puño.jpeg'
        base64_image = encode_image(image_path)
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": "En una imagen donde se muestra una mano con los dedos extendidos, ¿qué movimiento esperas que haga la mano? Si la mano se cierra, devuelve 1. Si la mano se abre, devuelve 0. Si es un movimiento de pinzas, devuelve 2."},
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                    },
                ],
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content