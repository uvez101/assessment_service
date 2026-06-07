from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
import os

# استدعاء الـ Schemas اللي بتحدد شكل الداتا
from schemas.request import AssessmentRequest
from schemas.response import AssessmentResponse, EvaluationReport

# استدعاء الـ Services اللي فيها اللوجيك
from services.assessment_gen import process_assessment_generation
# from services.auto_scoring import process_evaluation # هنفعل السطر ده لما نكتب ملف التصحيح

from services.auto_scoring import process_evaluation
from schemas.request import EvaluationRequest

router = APIRouter()

# ==========================================
# إعدادات الحماية (API Key) لحماية الـ Microservice
# ==========================================
API_KEY = os.getenv("SERVICE_API_KEY", "super_secret_key_123")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=403, detail="Could not validate API Key. Access Denied."
    )

# ==========================================
# 1. Endpoint التوليد (Generate Assessment)
# ==========================================
@router.post("/generate", response_model=AssessmentResponse, dependencies=[Depends(get_api_key)])
async def generate_assessment(request: AssessmentRequest):
    """
    بيستقبل متطلبات الوظيفة والمهارات، وبيكلم Hugging Face عشان يولد الأسئلة.
    """
    return process_assessment_generation(request)


# ==========================================
# 2. Endpoint التقييم (Evaluate & Score)
# ==========================================
@router.post("/evaluate", response_model=EvaluationReport, dependencies=[Depends(get_api_key)])
async def evaluate_assessment(request: EvaluationRequest):
    """
    بيستقبل إجابات المطور، بيصححها بـ Groq، وبيستخرج الـ Skill Gaps الحقيقية
    """
    return process_evaluation(request)
