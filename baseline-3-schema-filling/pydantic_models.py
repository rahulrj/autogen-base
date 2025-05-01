
from pydantic import BaseModel
import json

class PHQ9StructuredOutput(BaseModel):
    loss_of_interest: int
    feeling_down: int
    sleep_problems: int
    energy_level: int
    appetite_change: int
    self_worth: int
    concentration_difficulty: int
    motor_activity_change: int
    suicidal_thoughts: int

    @classmethod
    def from_raw_json(cls, raw_json_str):
        data = json.loads(raw_json_str)
        return cls(**data)



class TreatmentRecommendationResponse(BaseModel):
    severity: str
    recommendation: str
