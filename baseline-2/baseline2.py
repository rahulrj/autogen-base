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
from agent import *



# Process all depression descriptions and evaluate performance
all_results = []
true_labels = []
predicted_labels = []
error_from_llm = 0

for text_sample in DEPRESSION_DESCRIPTIONS:
    mapped_response = map_to_phq9(text_sample)
    phq9_score = compute_phq9_score(mapped_response)
    recommendation = generate_recommendation(phq9_score)

    if(recommendation.recommendation == "Error from LLM"):
        error_from_llm +=1
        continue

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
        "f1_score": f1,
        "error_from_llm": error_from_llm
    }
}

with open("output.json", "w") as json_file:
    json.dump(final_output, json_file, indent=4)

# Print results
print(json.dumps(final_output, indent=4))




