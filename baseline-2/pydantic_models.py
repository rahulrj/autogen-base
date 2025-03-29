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
    score: int = Field(..., ge=0, le=4)  # Score (0-4)

class PHQ9Response(BaseModel):
    responses: List[PHQ9Entry]  # List of PHQ-9 responses
    total_score: int = Field(..., ge=0, le=36)  # PHQ-9 total score

    @classmethod
    def ensure_valid_response(cls, responses: List[PHQ9Entry]):
        """Ensure structured response follows PHQ-9 format."""
        if not responses:
            responses = [PHQ9Entry(phq="Unknown", symptom="No symptoms detected", score=0)]
        total_score = sum(entry.score for entry in responses)
        return cls(responses=responses, total_score=total_score)




class PHQ9ScoreResponse(BaseModel):
    total_score: int = Field(..., ge=0, le=36)  # PHQ-9 total score
    classification: str  # "Not Depressed", "Mildly Depressed", "Quite Depressed"

    @classmethod
    def from_phq9_response(cls, phq9_response: PHQ9Response):
        """Convert PHQ9Response to PHQ9ScoreResponse"""
        return cls(total_score=phq9_response.total_score, classification=classify_depression(phq9_response.total_score))

def classify_depression(total_score: int) -> str:
    """Classify depression based on total PHQ-9 score"""
    if total_score < 4:
        return "Not Depressed"
    elif total_score <= 10:
        return "Mildly Depressed"
    else:
        return "Quite Depressed"




class TreatmentRecommendationResponse(BaseModel):
    recommendation: str  # "No treatment necessary", "Counseling", "Pharmaceutical Therapy"

    @classmethod
    def from_phq9_score(cls, phq9_score: PHQ9ScoreResponse):
        """Determine recommendation based on PHQ-9 score"""
        if phq9_score.total_score < 4:
            return cls(recommendation="No treatment necessary")
        elif phq9_score.total_score <= 10:
            return cls(recommendation="Counseling")
        else:
            return cls(recommendation="Pharmaceutical Therapy")
