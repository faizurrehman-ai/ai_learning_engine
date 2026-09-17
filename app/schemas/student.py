from pydantic import BaseModel, ConfigDict
from typing import Optional

# --- Student Schemas ---
class StudentCreate(BaseModel):
    name: str
    email: str
    track_id: str = "ai_ds"
    learning_speed: float = 1.0

class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    track_id: str
    learning_speed: float

# --- Performance Signal Schemas ---
class QuizSubmission(BaseModel):
    student_id: int
    concept_id: str
    score: float

class CodeReviewSubmission(BaseModel):
    student_id: int
    case_study_id: str
    code_quality_score: float
    mentor_feedback: Optional[str] = None

class ActivityLogCreate(BaseModel):
    student_id: int
    attendance_rate: float = 1.0
    github_commits: int = 0
    hours_logged: float = 0.0