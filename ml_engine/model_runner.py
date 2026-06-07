import os
import json
from groq import Groq
from dotenv import load_dotenv  # 1. استدعاء المكتبة

# 2. تحميل كل المتغيرات اللي في ملف .env عشان البايثون يشوفها
load_dotenv()
# بنقرا الـ Token من متغيرات البيئة
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# تهيئة الـ Client الخاص بـ Groq
client = Groq(api_key=GROQ_API_KEY)

# استخدام موديل Llama 3 لأنه ممتاز جداً في الالتزام بالـ JSON وسريع جداً على Groq
MODEL_ID = "llama-3.1-8b-instant"
# تقدر تستخدم "mixtral-8x7b-32768" لو حابب نفس عائلة Mistral اللي كنا شغالين بيها

def generate_questions_from_hf(prompt: str) -> list:
    try:
        # إرسال الطلب لـ Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=MODEL_ID,
            temperature=0.2,     # حرارة منخفضة للدقة
            max_tokens=1500,     # مساحة كافية للأسئلة
        )
        
        # استخراج النص اللي راجع من الموديل
        raw_text = chat_completion.choices[0].message.content.strip()
        
        # تنظيف النص من أي علامات Markdown
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.replace("```", "").strip()
            
        # تحويل النص لـ Python List أو Object
        result_data = json.loads(raw_text)
        return result_data
        
    except json.JSONDecodeError as e:
        # لو الموديل خرف ورجع نص مش JSON سليم
        print(f"Failed to parse JSON from Groq: {e}")
        print(f"Raw Output was: {raw_text}")
        return []
        
    except Exception as e:
        # لو فيه مشكلة في الاتصال بـ Groq
        print(f"Error calling Groq API: {e}")
        return []