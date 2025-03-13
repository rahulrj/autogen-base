from autogen_agentchat.agents import AssistantAgent
import random
import requests
import re
from tenacity import retry, wait_exponential, stop_after_attempt
from typing import Dict
from prompt import *
from keys import *
from prompt import GROUND_TRUTH_LABELS
from pydantic_models import *
import json
import re

class HuggingFaceAPIClient:
    def __init__(self, api_key, model="mistralai/Mistral-7B-Instruct-v0.2"):
        self.api_key = api_key
        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
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
hf_client = HuggingFaceAPIClient(api_key=HUGGINGFACE_KEY2)



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


def map_to_phq9(text_sample) -> PHQ9Response:
    """Extract PHQ-9 symptoms and return structured output in the new format."""
    mapping_prompt = PHQ9_MAPPING_PROMPT_NEW.format(text_sample=text_sample)
    response_text = schema_mapping_agent.generate_reply(
        messages=[{"role": "user", "content": mapping_prompt}]
    )

    print("DEBUG - Raw LLM Response:", response_text)  # Debugging

    try:
        # **Extract Only the JSON Object**
        json_match = re.search(r"\[.*\]", response_text, re.DOTALL)  # Adjusted for list format
        if json_match:
            json_response = json.loads(json_match.group())
        else:
            print("ERROR - No valid JSON detected!")
            return PHQ9Response.ensure_valid_response([])

        # **Parse Symptoms into PHQ9Response format**
        extracted_responses = []
        for entry in json_response:
            if isinstance(entry, dict) and "category" in entry and "symptom" in entry and "score" in entry:
                phq_category = PHQ9_CATEGORY_MAPPING.get(entry["category"], "Unknown")
                extracted_responses.append(
                    PHQ9Entry(phq=phq_category, symptom=entry["symptom"], score=entry["score"])
                )

        return PHQ9Response.ensure_valid_response(extracted_responses)

    except json.JSONDecodeError:
        print("ERROR - Invalid JSON format from LLM!")
        return PHQ9Response.ensure_valid_response([])




def compute_phq9_score(phq9_response: PHQ9Response) -> PHQ9ScoreResponse:
    """Compute the PHQ-9 total score and classification using structured response"""
    return PHQ9ScoreResponse.from_phq9_response(phq9_response)



def generate_recommendation(phq9_score: PHQ9ScoreResponse) -> TreatmentRecommendationResponse:
    """Generate treatment recommendation using structured response"""
    return TreatmentRecommendationResponse.from_phq9_score(phq9_score)



# Example usage
text_sample = get_depression_description()
mapped_response = map_to_phq9(text_sample)
phq9_score = compute_phq9_score(mapped_response)
recommendation = generate_recommendation(phq9_score)



print("GENERATED TEXT SAMPLES\n",text_sample)
print("MAPPED_RESPONSE_TO_PHQ9\n", mapped_response)
print("PHQ-9 SCORE AND CLASSIFICATION\n", phq9_score)
print("TREATMENT RECOMMENDATION\n", recommendation)



