from schemas.request import AssessmentRequest
from schemas.response import AssessmentResponse, Question
from ml_engine.prompt_builder import build_assessment_prompt
from ml_engine.model_runner import generate_questions_from_hf


def process_assessment_generation(request: AssessmentRequest) -> AssessmentResponse:
    # 1. تجهيز الـ Prompt بناءً على البيانات اللي جاية من الـ Node.js
    prompt = build_assessment_prompt(
        job_title=request.job_title,
        skills=request.skills,
        phase=request.phase,
        job_description=request.job_description
    )
    
    # 2. إرسال الطلب لموديل Hugging Face
    raw_questions = generate_questions_from_hf(prompt)
    
    # 3. التأكد من صحة البيانات (Validation) وتحويلها لـ Pydantic Objects
    validated_questions = []
    
    if not raw_questions:
        # Fallback: لو الموديل مرجعش حاجة (أو حصل إيرور)، بنرجع سؤال افتراضي 
        # عشان السيستم ما يقعش في وش المستخدم
        error_question = Question(
            question_text="Error: Could not generate assessment at this time. Please try again.",
            question_type="mcq" if request.phase == 1 else "essay",
            options=["A", "B", "C", "D"] if request.phase == 1 else None,
            correct_answer="A",
            explanation="System fallback due to AI generation failure."
        )
        validated_questions.append(error_question)
    else:
        # لو الداتا رجعت سليمة، بنغلفها جوه الـ Schema بتاعتنا
        for q in raw_questions:
            try:
                validated_q = Question(
                    question_text=q.get("question_text", "Missing question text"),
                    question_type=q.get("question_type", "mcq" if request.phase == 1 else "essay"),
                    options=q.get("options"),
                    correct_answer=q.get("correct_answer", "Missing correct answer"),
                    explanation=q.get("explanation", "No explanation provided")
                )
                validated_questions.append(validated_q)
            except Exception as e:
                print(f"Error validating question: {e}")
                continue # لو سؤال واحد فيه مشكلة، نتخطاه ونكمل الباقي
                
    # 4. تغليف النتيجة النهائية في الـ AssessmentResponse
    response = AssessmentResponse(
        job_title=request.job_title,
        phase=request.phase,
        questions=validated_questions
    )
    
    return response