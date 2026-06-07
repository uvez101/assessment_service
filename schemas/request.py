from pydantic import BaseModel
from typing import List, Optional


class AssessmentRequest(BaseModel):
    job_title: str
    job_description: Optional[str] = None  
    skills: List[str]
    experience_level: str  # مثال: Junior, Mid-Level, Senior
    phase: int  # 1 for initial quiz, 2 for advanced assessment


class AnswerItem(BaseModel):
    question_text: str
    user_answer: str


class EvaluationRequest(BaseModel):
    developer_id: str
    job_title: str
    phase: int
    answers: List[AnswerItem]
    cheat_flags: List[str] = []    