import random
import requests
import json
import re
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from tenacity import retry, wait_exponential, stop_after_attempt
from typing import List
from autogen_agentchat.agents import AssistantAgent
import tiktoken 

# HuggingFace API Client
class HuggingFaceAPIClient:
    def __init__(self, api_key, model="mistralai/Mistral-7B-Instruct-v0.2"):
        self.api_key = api_key
        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    def generate(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 150, "temperature": 0.7, "top_p": 0.9}}
        response = requests.post(self.api_url, headers=headers, json=payload)
        json_response = response.json()

        # Estimate token usage
        prompt_tokens = self.estimate_tokens(prompt)
        completion_tokens = self.estimate_tokens(json_response[0]["generated_text"]) if json_response else 0

        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens

        return json_response


    def estimate_tokens(self, text):
        """Estimate token usage using tiktoken (for OpenAI-like models)."""
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))


# Custom AssistantAgent Wrapper
class CustomAssistantAgent(AssistantAgent):
    def __init__(self, name, system_message, model_client):
        super().__init__(name=name, system_message=system_message, model_client=model_client)
        self._model_client = model_client  # Ensure compatibility with AutoGen internals

    def generate_reply(self, messages, **kwargs):
        user_input = messages[-1]["content"]
        response = self._model_client.generate(user_input)
        return response[0]["generated_text"] if response else "Error: No response"