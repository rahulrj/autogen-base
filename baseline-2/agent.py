
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
from client import *



# Initialize Hugging Face API Client
hf_client = HuggingFaceAPIClient(api_key=HUGGINGFACE_KEY2)

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
        json_match = re.search(r"DO NOT WRITE ANY TEXT AFTER THE JSON OUTPUT\.\s*(\[\s*{.*?}\s*\])\s*$", response_text, re.S)

        if json_match:
            json_text = json_match.group(1)
            extracted_json = json.loads(json_text)


            extracted_responses = []
            for entry in extracted_json:
                if isinstance(entry, dict) and "category" in entry and "symptom" in entry and "score" in entry:
                    phq_category = PHQ9_CATEGORY_MAPPING.get(entry["category"], "Unknown")
                    extracted_responses.append(
                        PHQ9Entry(phq=phq_category, symptom=entry["symptom"], score=entry["score"])
                    )

            return PHQ9Response.ensure_valid_response(extracted_responses)

        else:
            print("ERROR - No valid JSON detected!")
            return PHQ9Response.ensure_valid_response([])


    except json.JSONDecodeError as e:
        print("ERROR - Invalid JSON format from LLM!")
        return PHQ9Response.ensure_valid_response([])



def compute_phq9_score(phq9_response: PHQ9Response) -> PHQ9ScoreResponse:
    total_score = phq9_response.total_score
    score_prompt = SCORE_PROMPT.format(total_score=total_score)
    response_text = scoring_agent.generate_reply(messages=[{"role": "user", "content": score_prompt}])

    try:
        match = re.search(r"Classification:\s*(Not Depressed|Mildly Depressed|Quite Depressed|Error)", response_text, re.IGNORECASE)
        if match:
            classification = match.group(1)
            return PHQ9ScoreResponse.ensure_valid_response(total_score,classification)
        else:
            return PHQ9ScoreResponse.ensure_valid_response(total_score,"Error")
    except:
        return PHQ9ScoreResponse.ensure_valid_response(total_score,"Error")





# Generate treatment recommendation
def generate_recommendation(phq9_score: PHQ9ScoreResponse) -> TreatmentRecommendationResponse:
    recommendation_prompt = RECOMMENDATION_PROMPT.format(phq9_score=phq9_score.total_score)
    response_text = recommendation_agent.generate_reply(messages=[{"role": "user", "content": recommendation_prompt}])

    try:
        match = re.search(r"Recommendation:\s*(Error from LLM|No treatment necessary|Counseling|Pharmaceutical Therapy)", response_text, re.IGNORECASE)
        if match:
            recommendation = match.group(1).strip().title()
            print("RECOMMENDATION", recommendation)
            return TreatmentRecommendationResponse.ensure_valid_response(recommendation=recommendation)
        else:
            return TreatmentRecommendationResponse.ensure_valid_response("Error from LLM")
    except:
        return TreatmentRecommendationResponse.ensure_valid_response("Error from LLM")





