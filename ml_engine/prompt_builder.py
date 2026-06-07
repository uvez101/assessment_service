def build_assessment_prompt(job_title: str, skills: list, phase: int, job_description: str = None) -> str:
    # التأكد من وجود مهارات أو وضع نص افتراضي
    skills_str = ", ".join(skills) if skills else "General technical skills"

    # دمج المهارات ووصف الوظيفة كمرجع أساسي لا يمكن للموديل تجاهله
    context = f"Job Title: {job_title}\n"
    if skills:
        context += f"Candidate/Required Skills: {skills_str}\n"
    if job_description:
        context += f"HR Job Context & Requirements: {job_description}\n"

    # تحديد مستوى الصعوبة ونوع الأسئلة بناءً على المرحلة
    if phase == 1:
        difficulty_context = (
            "Create 5 Multiple-Choice Questions (MCQs) to test foundational and intermediate knowledge. "
            "CRITICAL: Every question MUST be strictly derived from the provided Skills or HR Job Context above. Do not ask generic questions."
        )
        json_format = """
        {
            "question_text": "The text of the MCQ question",
            "question_type": "mcq",
            "options": ["Option A", "Option B", "Option C", "Option D"], 
            "correct_answer": "The exact text of the correct option",
            "explanation": "Why this is correct (useful for learning paths)"
        }
        """
    else:
        difficulty_context = (
            "Create 3 Advanced Scenario-based Essay questions. "
            "CRITICAL: Do NOT ask the candidate to write any syntax or live code. Focus on architecture, problem-solving, and conceptual understanding. "
            "Every scenario MUST be strictly tailored to the provided Skills or HR Job Context above."
        )
        json_format = """
        {
            "question_text": "The scenario-based essay question text",
            "question_type": "essay",
            "options": null, 
            "correct_answer": "The key concepts or bullet points expected in an ideal essay answer",
            "explanation": "Detailed explanation of the ideal solution (useful for HR evaluation)"
        }
        """

    # أمر التوليد النهائي مع إجبار الموديل على شكل الـ JSON
    prompt = f"""
    You are an expert Technical Interviewer and AI Recruitment Specialist.
    Based STRICTLY on the following profile and job requirements:
    
    {context}
    
    {difficulty_context}
    
    You MUST return the result EXACTLY as a valid JSON array of objects. Do not include any markdown formatting, greetings, or explanations outside the JSON.
    Format each question in the array exactly like this:
    [
        {json_format}
    ]
    """
    return prompt

# --- الدالة المفقودة التي كانت تسبب الـ ImportError ---

def build_evaluation_prompt(job_title: str, phase: int, answers_data: list) -> str:
    # تحويل الإجابات لنص يحتوي على الإجابة النموذجية (Ground Truth)
    answers_text = ""
    for i, ans in enumerate(answers_data, 1):
        # بنضيف الإجابة النموذجية اللي كانت موجودة أصلاً في الـ JSON بتاع التوليد
        answers_text += f"--- Question {i} ---\n"
        answers_text += f"Text: {ans.question_text}\n"
        answers_text += f"Model Correct Answer: {ans.correct_answer}\n"
        answers_text += f"Candidate's Answer: {ans.user_answer}\n\n"

    json_format = """
    {
        "correct_answers": int,
        "wrong_answers": int,
        "skill_gaps": [
            {"skill_name": "string", "failed_questions_count": int, "recommended_topic_to_study": "string"}
        ],
        "general_feedback": "string"
    }
    """

    prompt = f"""
    You are an expert Technical Interviewer for the role: {job_title}.
    Your task is to grade the candidate's answers by comparing them strictly against the 'Model Correct Answer'.
    
    CRITICAL RULES:
    1. If the candidate's answer is semantically equivalent to the 'Model Correct Answer', mark it as correct.
    2. Do not be biased. If the answer is partially correct but misses key concepts, count it as wrong and explain why.
    3. For every wrong answer, identify the specific skill gap and provide a concrete study topic.

    {answers_text}
    
    Return ONLY valid JSON with this structure:
    {json_format}
    """
    return prompt