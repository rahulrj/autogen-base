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

# Pydantic Models
class PHQ9Response(BaseModel):
    @classmethod
    def ensure_valid_response(cls, symptoms: Dict[str, int]):
        if not symptoms:  # If symptoms are empty, provide default values
            symptoms = {"Unknown symptom": 0}
        total_score = sum(symptoms.values())
        classification = (
            "Not Depressed" if total_score < 4 else
            "Mildly Depressed" if total_score <= 10 else
            "Quite Depressed"
        )
        return cls(symptoms=symptoms, total_score=total_score, classification=classification)

    symptoms: Dict[str, int]  # Dictionary of symptom names and their scores
    total_score: int = Field(..., ge=0, le=36)  # Ensures total score is within valid range
    classification: str  # Expected output: "Not Depressed", "Mildly Depressed", "Quite Depressed"



class TreatmentRecommendation(BaseModel):
    recommendation: str  # Should only contain: "No treatment necessary", "Counseling", or "Pharmaceutical Therapy"



class EvaluationResult(BaseModel):
    predicted_label: str  # The predicted classification
    ground_truth_label: str  # The correct label
    evaluation: str  # Should only be "Correct" or "Incorrect"



class StructuredOutput(BaseModel):
    generated_text_sample: str
    mapped_response: PHQ9Response
    treatment_recommendation: TreatmentRecommendation
    ground_truth_label: str
    evaluation_result: EvaluationResult



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
def map_to_phq9(text_sample) -> PHQ9Response:
    """Extract symptoms and PHQ-9 scores from the response, ensuring a valid response."""
    mapping_prompt = PHQ9_MAPPING_PROMPT.format(text_sample=text_sample)
    response_text = schema_mapping_agent.generate_reply(
        messages=[{"role": "user", "content": mapping_prompt}]
    )
    
    try:
        symptoms = {}
        for line in response_text.split("\n"):
            match = re.search(r"(.+?):\s*\(?([0-4])\)?", line)  # Extract symptom and score
            if match:
                symptom, score = match.groups()
                symptoms[symptom.strip()] = int(score)

        total_score = sum(symptoms.values())
        classification = (
            "Not Depressed" if total_score < 4 else
            "Mildly Depressed" if total_score <= 10 else
            "Quite Depressed"
        )

        return PHQ9Response.ensure_valid_response(symptoms)

    except Exception as e:
        return PHQ9Response(symptoms={}, total_score=0, classification="Error: Invalid Response")

# Function to generate treatment recommendations
def generate_recommendation(phq9_response: PHQ9Response) -> TreatmentRecommendation:
    recommendation = (
        "No treatment necessary" if phq9_response.total_score < 4 else
        "Counseling" if phq9_response.total_score <= 10 else
        "Pharmaceutical Therapy"
    )
    return TreatmentRecommendation(recommendation=recommendation)

# Function to evaluate predictions against ground truth
def evaluate_predictions(text_sample: str, predicted_label: str) -> EvaluationResult:
    ground_truth_label = GROUND_TRUTH_LABELS.get(text_sample, "Unknown")
    evaluation = "Correct" if predicted_label == ground_truth_label else "Incorrect"
    return EvaluationResult(predicted_label=predicted_label, ground_truth_label=ground_truth_label, evaluation=evaluation)

# Example usage
text_sample = get_depression_description()
mapped_response = map_to_phq9(text_sample)  # Now returns PHQ9Response object
recommendation = generate_recommendation(mapped_response)  # Now returns TreatmentRecommendation object
evaluation_result = evaluate_predictions(text_sample, mapped_response.classification)  # Returns EvaluationResult object

structured_output = StructuredOutput(
    generated_text_sample=text_sample,
    mapped_response=mapped_response,
    treatment_recommendation=recommendation,
    ground_truth_label=evaluation_result.ground_truth_label,
    evaluation_result=evaluation_result
)

# Save structured output to JSON file
import json
with open("output.json", "w") as json_file:
    json.dump(structured_output.model_dump(), json_file, indent=4)

# Print structured results
print(structured_output.model_dump_json(indent=4))
