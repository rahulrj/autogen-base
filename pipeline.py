from autogen_agentchat.agents import AssistantAgent
import random
from prompt import *


import requests

class HuggingFaceAPIClient:
    def __init__(self, api_key, model="mistralai/Mistral-7B-Instruct-v0.2"):
        self.api_key = api_key
        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
    
    def generate(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }
        response = requests.post(self.api_url, headers=headers, json=payload)
        return response.json()

# Example usage
hf_client = HuggingFaceAPIClient(api_key="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")

# Custom AssistantAgent Wrapper
class CustomAssistantAgent(AssistantAgent):
    def __init__(self, name, system_message, model_client):
        super().__init__(name=name, system_message=system_message, model_client=model_client)
        self._model_client = model_client  # Ensure compatibility with AutoGen internals
    
    def generate_reply(self, messages, **kwargs):
        user_input = messages[-1]["content"]
        response = self._model_client.generate(user_input)
        return response[0]["generated_text"] if response else "Error: No response"

# Step 2: Schema Mapping Agent
schema_mapping_agent = CustomAssistantAgent(
    name="Schema_Mapping_Agent",
    system_message="Extract symptoms from unstructured text and map them to the PHQ-9 categories with corresponding scores (0-4).",
    model_client=hf_client
)

# Step 3: Scoring Agent
scoring_agent = CustomAssistantAgent(
    name="Scoring_Agent",
    system_message="Analyze the PHQ-9 responses and compute the total depression score.",
    model_client=hf_client
)

# Step 4: Recommendation Agent
recommendation_agent = CustomAssistantAgent(
    name="Recommendation_Agent",
    system_message="Provide treatment recommendations based on the PHQ-9 score.",
    model_client=hf_client
)

# Function to get a depression description from a hardcoded list
def get_depression_description():
    return random.choice(DEPRESSION_DESCRIPTIONS)

# Function to map descriptions to PHQ-9 categories with scores
def map_to_phq9(text_sample):
    mapping_prompt = PHQ9_MAPPING_PROMPT.format(text_sample=text_sample)
    phq9_mapped_responses = schema_mapping_agent.generate_reply(
        messages=[{"role": "user", "content": mapping_prompt}]
    )
    return phq9_mapped_responses

# Function to compute PHQ-9 total score and classify depression severity
def compute_phq9_score(phq9_responses):
    score_prompt = SCORE_PROMPT.format(phq9_responses=phq9_responses)
    score_analysis = scoring_agent.generate_reply(
        messages=[{"role": "user", "content": score_prompt}]
    )
    return score_analysis

# Function to generate treatment recommendations
def generate_recommendation(phq9_score):
    recommendation_prompt = RECOMMENDATION_PROMPT.format(phq9_score=phq9_score)
    recommendation = recommendation_agent.generate_reply(
        messages=[{"role": "user", "content": recommendation_prompt}]
    )
    return recommendation

# Example usage
text_sample = get_depression_description()
mapped_response = map_to_phq9(text_sample)
phq9_score = compute_phq9_score(mapped_response)
recommendation = generate_recommendation(phq9_score)

print("GENERATED TEXT SAMPLES:**********************************", text_sample)
print("MAPPED_RESPONSE_TO_PHQ9:********************************", mapped_response)
print("PHQ-9 SCORE AND CLASSIFICATION:********************************", phq9_score)
print("TREATMENT RECOMMENDATION:********************************", recommendation)












