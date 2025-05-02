import requests
from tenacity import retry, wait_exponential, stop_after_attempt
from prompt import *
import re
from keys import *
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from collections import defaultdict
from typing import List
from tqdm import tqdm


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



def generate_schema_from_task(hf_client: HuggingFaceAPIClient) -> str:
    prompt = SCHEMA_GEN_PROMPT_TEMPLATE.strip()
    response = hf_client.generate(prompt)
    generated_text = response[0]["generated_text"]

    print("\n=== LLM-Generated Schema ===\n")
    print(generated_text)

    return generated_text



def build_prompt_from_input(input_text: str) -> str:
    return SCHEMA_GEN_PROMPT_TEMPLATE.format(input_text=input_text).strip()



def extract_json_schema(text: str) -> dict:
    matches = list(re.finditer(r"\{[\s\S]*?\}", text))
    if not matches:
        raise ValueError("No JSON object found in LLM output.")
    
    last_match = matches[-1]
    json_str = text[last_match.start():last_match.end()]
    
    try:
        schema = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")
    
    return schema



def score_generated_schema(generated_schema: dict) -> dict:
    generated_keys = set(generated_schema.keys())
    
    matched_keys = generated_keys & EXPECTED_PHQ9_KEYS
    extra_keys = generated_keys - EXPECTED_PHQ9_KEYS
    missing_keys = EXPECTED_PHQ9_KEYS - generated_keys

    score = len(matched_keys) / len(EXPECTED_PHQ9_KEYS)

    return {
        "score": round(score, 2),
        "matched": list(matched_keys),
        "missing": list(missing_keys),
        "extra": list(extra_keys),
        "total_keys": len(generated_keys)
    }


def run_schema_eval_on_samples(hf_client, samples: List[str]):
    results = []
    for text in tqdm(samples, desc="Evaluating Schemas"):
        prompt = build_prompt_from_input(text)
        try:
            response = hf_client.generate(prompt)
            print("RESPONSE", response)
            raw_output = response[0]["generated_text"]
            extracted_schema = extract_json_schema(raw_output)
            score_result = score_generated_schema(extracted_schema)
        except Exception as e:
            score_result = {
                "error": str(e),
                "score": 0.0,
                "matched": [],
                "missing": list(EXPECTED_PHQ9_KEYS),
                "extra": [],
                "total_keys": 0
            }
            raw_output = ""
            extracted_schema = {}

        results.append({
            "input_text": text,
            "generated_output": raw_output,
            "schema": extracted_schema,
            "score_result": score_result
        })

    with open("schema_eval_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results




def compute_overall_schema_metrics(results: List[dict]):
    y_true = []
    y_pred = []

    for r in results:
        gold_keys = set(EXPECTED_PHQ9_KEYS)
        pred_keys = set(r["schema"].keys())

        for key in gold_keys:
            y_true.append(1)
            y_pred.append(1 if key in pred_keys else 0)

        for key in pred_keys:
            if key not in gold_keys:
                y_true.append(0)
                y_pred.append(1)

    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    accuracy = accuracy_score(y_true, y_pred)

    print("\n=== Overall Schema Metrics ===")
    print(f"Accuracy: {accuracy:.2f}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1 Score: {f1:.2f}")

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }


if __name__ == "__main__":
    hf_client = HuggingFaceAPIClient(HUGGINGFACE_KEY2)
    
    results = run_schema_eval_on_samples(hf_client, DEPRESSION_INPUTS)
    metrics = compute_overall_schema_metrics(results)

    with open("output.json", "w") as json_file:
        json.dump(metrics, json_file, indent=4)

    # Optionally save to file
    with open("schema_eval_output.json", "w") as f:
        json.dump(results, f, indent=2)