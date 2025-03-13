from autogen_agentchat.agents import AssistantAgent
import random
import requests
import json
import re
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from prompt import *
from keys import *

# HuggingFace API Client with Retry
class HuggingFaceAPIClient:
    def __init__(self, api_key, model="mistralai/Mistral-7B-Instruct-v0.1"):
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

# Initialize HuggingFace Client
hf_client = HuggingFaceAPIClient(api_key=HUGGINGFACE_KEY2)

# Custom AssistantAgent Wrapper
class CustomAssistantAgent(AssistantAgent):
    def __init__(self, name, system_message, model_client):
        super().__init__(name=name, system_message=system_message, model_client=model_client)
        self._model_client = model_client  # Ensure compatibility with AutoGen internals

    def generate_reply(self, messages, **kwargs):
        user_input = messages[-1]["content"]
        response = self._model_client.generate(user_input)
        print("\033[1mDEBUG - Raw LLM Response:\033[0m", response)
        return response[0]["generated_text"] if response else "Error: No response"

# Initialize Agents
schema_mapping_agent = CustomAssistantAgent(
    name="Schema_Mapping_Agent",
    system_message="Extract symptoms from unstructured text and map them to PHQ-9 categories with corresponding scores (0-4). Respond with a structured JSON format.",
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

# Function to map descriptions to PHQ-9 categories with scores
def map_to_phq9(text_sample):
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

        return {"symptoms": symptoms, "total_score": total_score, "classification": classification}

    except Exception as e:
        return {"symptoms": {}, "total_score": 0, "classification": "Error: Invalid Response"}

# Function to compute PHQ-9 total score and classify depression severity
def compute_phq9_score(mapped_response):
    score_prompt = SCORE_PROMPT.format(phq9_responses=mapped_response)
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

# Function to evaluate predictions against ground truth
def evaluate_predictions(text_sample, predicted_label):
    ground_truth_label = GROUND_TRUTH_LABELS.get(text_sample, "Unknown")
    evaluation = "Correct" if predicted_label == ground_truth_label else "Incorrect"
    return {"predicted_label": predicted_label, "ground_truth_label": ground_truth_label, "evaluation": evaluation}

# Process Multiple Samples and Compute Metrics
all_results = []
true_labels = []
predicted_labels = []

for text_sample in DEPRESSION_DESCRIPTIONS:
    mapped_response = map_to_phq9(text_sample)
    phq9_score = compute_phq9_score(mapped_response)
    recommendation = generate_recommendation(phq9_score)
    evaluation_result = evaluate_predictions(text_sample, mapped_response["classification"])

    structured_output = {
        "generated_text_sample": text_sample,
        "mapped_response": mapped_response,
        "treatment_recommendation": recommendation,
        "ground_truth_label": evaluation_result["ground_truth_label"],
        "evaluation_result": evaluation_result
    }

    all_results.append(structured_output)
    true_labels.append(evaluation_result["ground_truth_label"])
    predicted_labels.append(mapped_response["classification"])

# Compute Metrics
accuracy = accuracy_score(true_labels, predicted_labels)
precision = precision_score(true_labels, predicted_labels, average="weighted", zero_division=1)
recall = recall_score(true_labels, predicted_labels, average="weighted", zero_division=1)
f1 = f1_score(true_labels, predicted_labels, average="weighted", zero_division=1)

# Save Results
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

# Print Results
print(json.dumps(final_output, indent=4))
