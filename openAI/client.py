import openai
import openai.resources

class OpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key


    def create_completion(self, prompt, model="gpt-4o-mini", max_tokens=50):
        print(model)
        print(prompt)
        print(max_tokens)
    
        print(chat_completion.choices)
        message_content = chat_completion.choices[0].message.content
        print(message_content)
        return chat_completion