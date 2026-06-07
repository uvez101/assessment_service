import os
import json
from dotenv import load_dotenv
from groq import Groq
from schemas.request import EvaluationRequest
from schemas.response import EvaluationReport, SkillGap
from ml_engine.prompt_builder import build_evaluation_prompt

# 1. تحميل مفتاح Groq بأمان
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def process_evaluation(request: EvaluationRequest) -> EvaluationReport:
    total_q = len(request.answers)
    job_title = request.job_title if request.job_title else "Unspecified Role"

    # 2. بناء الـ Prompt
    prompt = build_evaluation_prompt(
        job_title=job_title,
        phase=request.phase,
        answers_data=request.answers
    )

    try:
        # 3. إرسال الطلب لـ Groq للتصحيح
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",  # نفس الموديل السريع اللي شغالين بيه
            temperature=0.1,               # حرارة قليلة جداً للدقة
            max_tokens=1024,
        )
        raw_text = chat_completion.choices[0].message.content.strip()

        # تنظيف الـ JSON
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.replace("```", "").strip()

        # 4. قراءة نتيجة التصحيح
        ai_evaluation = json.loads(raw_text)
        
        correct = ai_evaluation.get("correct_answers", 0)
        wrong = ai_evaluation.get("wrong_answers", total_q)
        score_perc = (correct / total_q) * 100 if total_q > 0 else 0.0

        # تجهيز قائمة الفجوات المهارية الحقيقية من الموديل
        skill_gaps_list = []
        for gap in ai_evaluation.get("skill_gaps", []):
            skill_gaps_list.append(SkillGap(
                skill_name=gap.get("skill_name", "General Technical Skill"),
                failed_questions_count=gap.get("failed_questions_count", 1),
                recommended_topic_to_study=gap.get("recommended_topic_to_study", "Review core concepts.")
            ))

        general_feedback = ai_evaluation.get("general_feedback", "Evaluation completed.")

    except Exception as e:
        print(f"Error during AI evaluation: {e}")
        # خطة طوارئ لو حصل مشكلة
        correct = 0
        wrong = total_q
        score_perc = 0.0
        skill_gaps_list = []
        general_feedback = "Could not generate detailed AI feedback at this time."

    # 5. تغليف النتيجة النهائية
    return EvaluationReport(
        developer_id=request.developer_id,
        job_title=job_title,
        total_questions=total_q,
        correct_answers=correct,
        wrong_answers=wrong,
        score_percentage=round(score_perc, 2),
        cheat_flags=request.cheat_flags if request.cheat_flags else [],
        is_disqualified=len(request.cheat_flags) > 0 if request.cheat_flags else False,
        skill_gaps=skill_gaps_list,
        general_feedback=general_feedback
    )