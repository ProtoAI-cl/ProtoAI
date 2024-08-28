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
    
    def process_image(self, prompt, model , image_url):
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                    },
                    },
                ],
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content