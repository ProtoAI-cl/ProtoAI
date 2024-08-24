from openai import OpenAI

class OpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        OpenAI.api_key = self.api_key