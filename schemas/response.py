from pydantic import BaseModel
from typing import List, Optional

# الجزء الأول: توليد الأسئلة (Generation)

class Question(BaseModel):
    question_text: str
    question_type: str  # ضفنا دي (mcq أو essay)
    options: Optional[List[str]] = None  
    correct_answer: str
    explanation: str 


class AssessmentResponse(BaseModel):
    job_title: str
    phase: int  
    questions: List[Question]


# الجزء الثاني: تقييم الإجابات (Evaluation)

class SkillGap(BaseModel):
    skill_name: str
    failed_questions_count: int
    recommended_topic_to_study: str # ده اللي هيتبني عليه الـ Learning Path

class EvaluationReport(BaseModel):
    developer_id: str
    job_title: str
    
    # إحصائيات سريعة عن الأداء
    total_questions: int
    correct_answers: int
    wrong_answers: int
    score_percentage: float
    
    # مؤشرات الحماية من الغش
    cheat_flags: List[str] 
    is_disqualified: bool 
    
    # الفيدباك ومسارات التعلم
    skill_gaps: List[SkillGap] 
    general_feedback: str