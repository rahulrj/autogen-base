import requests
from tenacity import retry, wait_exponential, stop_after_attempt
from pydantic_models import *
from prompt import *
import re
from keys import *
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from collections import defaultdict

# Hugging Face API Client
class HuggingFaceAPIClient:
    def __init__(self, api_key, model="mistralai/Mistral-7B-Instruct-v0.3"):
        self.api_key = api_key
        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    def generate(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 300, "temperature": 0.7, "top_p": 0.9}}
        response = requests.post(self.api_url, headers=headers, json=payload)
        json_response = response.json()

        return json_response



# Function using HuggingFaceAPIClient
def call_llm(prompt, hf_client: HuggingFaceAPIClient):
    response = hf_client.generate(prompt)
    return response[0]["generated_text"]


def extract_last_json(text):
    """Extracts the last JSON object from text."""
    matches = list(re.finditer(r'\{[\s\S]*?\}', text))
    if matches:
        last_match = matches[-1]
        return text[last_match.start():last_match.end()]
    else:
        raise ValueError("No JSON object found in the LLM output.")



def map_to_structured_phq9(text_sample, hf_client: HuggingFaceAPIClient):
    prompt = FILL_PHQ9_PROMPT_TEMPLATE.format(text_sample=text_sample)
    response_text = call_llm(prompt, hf_client)

    print("\n=== RAW LLM Response ===\n")
    print(response_text)

    # Extract the last JSON object
    try:
        json_text = extract_last_json(response_text)
        structured_output = PHQ9StructuredOutput.from_raw_json(json_text)
        return structured_output
    except Exception as e:
        print(f"Error parsing LLM output: {e}")
        return None



def generate_treatment_recommendation_from_score(phq9_output: PHQ9StructuredOutput) -> TreatmentRecommendationResponse:
    # Calculate total score
    total_score = (
        phq9_output.loss_of_interest +
        phq9_output.feeling_down +
        phq9_output.sleep_problems +
        phq9_output.energy_level +
        phq9_output.appetite_change +
        phq9_output.self_worth +
        phq9_output.concentration_difficulty +
        phq9_output.motor_activity_change +
        phq9_output.suicidal_thoughts
    )

    # Map score to treatment
    if total_score < 4:
        recommendation = "No treatment necessary"
        severity = "Not Depressed"
    elif total_score <= 10:
        recommendation = "Counseling"
        severity = "Mildly Depressed"
    else:
        recommendation = "Pharmaceutical Therapy"
        severity = "Quite Depressed"

    return TreatmentRecommendationResponse(severity=severity, recommendation=recommendation)



def evaluate_depression_treatment(hf_client: HuggingFaceAPIClient):
    ground_truth_labels = []
    predicted_labels = []
    output_records = []

    for text_sample, ground_truth_label in DEPRESSION_TREATMENT_LABELS.items():
        
        structured_output = map_to_structured_phq9(text_sample, hf_client)
        if structured_output:
            treatment_recommendation = generate_treatment_recommendation_from_score(structured_output)
            predicted_label = treatment_recommendation.recommendation

            print(f"Ground Truth: {ground_truth_label}")
            print(f"Predicted: {predicted_label}")

            ground_truth_labels.append(ground_truth_label)
            predicted_labels.append(predicted_label)

            output_records.append({
                "text": text_sample,
                "ground_truth": ground_truth_label,
                "predicted": predicted_label
            })
        else:
            print("Skipping due to parsing error.")

    # Compute sklearn metrics
    accuracy = accuracy_score(ground_truth_labels, predicted_labels)
    precision = precision_score(ground_truth_labels, predicted_labels, average='weighted', zero_division=0)
    recall = recall_score(ground_truth_labels, predicted_labels, average='weighted', zero_division=0)
    f1 = f1_score(ground_truth_labels, predicted_labels, average='weighted', zero_division=0)

    # Save results
    result_summary = {
        "metrics": {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1
        }
    }

    with open("output.json", "w") as f:
        json.dump(result_summary, f, indent=2)

    print("\n=== Final Evaluation Results ===")
    print(f"Accuracy: {accuracy:.2%}")
    print(f"Precision: {precision:.2%}")
    print(f"Recall: {recall:.2%}")
    print(f"F1 Score: {f1:.2%}")

    return result_summary



if __name__ == "__main__":
    hf_client = HuggingFaceAPIClient(api_key=HUGGINGFACE_KEY2)
    results = evaluate_depression_treatment(hf_client)


