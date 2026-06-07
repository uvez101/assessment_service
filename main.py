# نقطة البداية (Entry point) للـ FastAPI
from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="AI Assessment Generator",
    description="API for auto-generating technical tests and evaluating candidates",
    version="1.0.0"
)

# هنا بنقول للـ FastAPI يقرأ الـ Endpoints اللي كتبناها في ملف الـ routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Assessment Service is running correctly!"}