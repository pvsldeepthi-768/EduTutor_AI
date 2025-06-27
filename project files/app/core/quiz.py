from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.services.quiz_generator import generate_quiz

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/generate")
async def generate_quiz_route(request: Request, topic: str = Form(...), difficulty: str = Form("medium")):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/auth/login")

    quiz_content = generate_quiz(topic, difficulty)
    # Save quiz to session for scoring later
    request.session["last_quiz"] = quiz_content

    return templates.TemplateResponse("quiz_questions.html", {
        "request": request,
        "quiz": quiz_content,
        "topic": topic,
        "difficulty": difficulty
    })
