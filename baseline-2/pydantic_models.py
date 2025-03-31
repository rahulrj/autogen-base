from pydantic import BaseModel, Field
from typing import List, Dict



# Mapping PHQ-9 category numbers to descriptions
PHQ9_CATEGORY_MAPPING = {
    "1": "Little interest or pleasure in doing things",
    "2": "Feeling down, depressed, or hopeless",
    "3": "Trouble falling or staying asleep, or sleeping too much",
    "4": "Feeling tired or having little energy",
    "5": "Poor appetite or overeating",
    "6": "Feeling bad about yourself or that you are a failure",
    "7": "Trouble concentrating on things",
    "8": "Moving or speaking so slowly that other people notice",
    "9": "Thoughts that you would be better off dead or hurting yourself in some way"
}

class PHQ9Entry(BaseModel):
    phq: str  # Mapped PHQ-9 category name
    symptom: str  # Extracted symptom description
    score: int = Field(..., ge=-1, le=4)  # Score (0-4)

class PHQ9Response(BaseModel):
    responses: List[PHQ9Entry]  # List of PHQ-9 responses
    total_score: int = Field(..., ge=-1, le=36)  # PHQ-9 total score

    @classmethod
    def ensure_valid_response(cls, responses: List[PHQ9Entry]):
        """Ensure structured response follows PHQ-9 format."""
        if not responses:
            responses = [PHQ9Entry(phq="Unknown", symptom="No symptoms detected", score=-1)]
        total_score = sum(entry.score for entry in responses)
        return cls(responses=responses, total_score=total_score)




class PHQ9ScoreResponse(BaseModel):
    total_score: int = Field(..., ge=-1, le=36)  # PHQ-9 total score
    classification: str  # "Not Depressed", "Mildly Depressed", "Quite Depressed", "Error"

    @classmethod
    def ensure_valid_response(cls, total_score, response):
        return cls(total_score=total_score, classification=response)




class TreatmentRecommendationResponse(BaseModel):
    recommendation: str  # "No treatment necessary", "Counseling", "Pharmaceutical Therapy"

    @classmethod
    def ensure_valid_response(cls, recommendation):
        return cls(recommendation=recommendation)
