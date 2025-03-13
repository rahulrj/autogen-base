from autogen_agentchat.agents import AssistantAgent
import random
import requests
import json
import re
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from tenacity import retry, wait_exponential, stop_after_attempt
from typing import List
from prompt import *
from keys import *
from prompt import GROUND_TRUTH_LABELS
from pydantic_models import *

# HuggingFace API Client
class HuggingFaceAPIClient:
    def __init__(self, api_key, model="mistralai/Mistral-7B-Instruct-v0.2"):
        self.api_key = api_key
        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    def generate(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 150, "temperature": 0.7, "top_p": 0.9}}
        response = requests.post(self.api_url, headers=headers, json=payload)
        return response.json()

# Initialize Hugging Face API Client
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

# Define Agents
schema_mapping_agent = CustomAssistantAgent(
    name="Schema_Mapping_Agent",
    system_message="Extract symptoms from unstructured text and map them to the PHQ-9 categories with corresponding scores (0-4).",
    model_client=hf_client
)

scoring_agent = CustomAssistantAgent(
    name="Scoring_Agent",
    system_message="Analyze the PHQ-9 responses and compute the total depression score.",
    model_client=hf_client
)

recommendation_agent = CustomAssistantAgent(
    name="Recommendation_Agent",
    system_message="Provide treatment recommendations based on the PHQ-9 score.",
    model_client=hf_client
)

# Function to process PHQ-9 mapping
def map_to_phq9(text_sample) -> PHQ9Response:
    mapping_prompt = PHQ9_MAPPING_PROMPT_NEW.format(text_sample=text_sample)
    response_text = schema_mapping_agent.generate_reply(messages=[{"role": "user", "content": mapping_prompt}])

    # print("DEBUG - Raw LLM Response:", response_text)  # Debugging

    try:
        json_match = re.search(r"\[.*\]", response_text, re.DOTALL)  # Extract list format
        if json_match:
            json_response = json.loads(json_match.group())
        else:
            print("ERROR - No valid JSON detected!")
            return PHQ9Response.ensure_valid_response([])

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

# Compute PHQ-9 score from response
def compute_phq9_score(phq9_response: PHQ9Response) -> PHQ9ScoreResponse:
    return PHQ9ScoreResponse.from_phq9_response(phq9_response)

# Generate treatment recommendation
def generate_recommendation(phq9_score: PHQ9ScoreResponse) -> TreatmentRecommendationResponse:
    return TreatmentRecommendationResponse.from_phq9_score(phq9_score)

# Process all depression descriptions and evaluate performance
all_results = []
true_labels = []
predicted_labels = []

for text_sample in DEPRESSION_DESCRIPTIONS:
    mapped_response = map_to_phq9(text_sample)
    phq9_score = compute_phq9_score(mapped_response)
    recommendation = generate_recommendation(phq9_score)

    true_labels.append(DEPRESSION_TREATMENT_LABELS.get(text_sample, "Unknown"))
    predicted_labels.append(recommendation.recommendation)

print(true_labels)
print(predicted_labels)

# Compute Evaluation Metrics
accuracy = accuracy_score(true_labels, predicted_labels)
precision = precision_score(true_labels, predicted_labels, average="weighted", zero_division=1)
recall = recall_score(true_labels, predicted_labels, average="weighted", zero_division=1)
f1 = f1_score(true_labels, predicted_labels, average="weighted", zero_division=1)

# Save results
final_output = {
    "results": all_results,
    "metrics": {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }
}

with open("output.json", "w") as json_file:
    json.dump(final_output, json_file, indent=4)

# Print results
print(json.dumps(final_output, indent=4))




