from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.diagnostic_engine import generate_diagnostic_test
from app.services.quiz_generator import generate_quiz
from app.core.pinecone_client import save_quiz_result
import json
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
async def student_dashboard(request: Request):
    user = request.session.get("user")
    courses = request.session.get("courses", [])
    if not user:
        return RedirectResponse(url="/auth/login")
    return templates.TemplateResponse("student_dashboard.html", {"request": request, "user": user, "courses": courses})

@router.post("/diagnostic_test")
async def start_diagnostic_test(request: Request, subject: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/auth/login")
    diagnostic_test = generate_diagnostic_test(subject)
    return templates.TemplateResponse("diagnostic_test.html", {"request": request, "test": diagnostic_test, "subject": subject})

@router.post("/generate_quiz")
async def generate_quiz_route(request: Request, topic: str = Form(...), difficulty: str = Form("medium")):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/auth/login")

    quiz = generate_quiz(topic, difficulty)
    request.session["last_quiz"] = quiz
    request.session["last_quiz_topic"] = topic
    request.session["last_quiz_difficulty"] = difficulty
    return templates.TemplateResponse("quiz_questions.html", {
        "request": request,
        "quiz": quiz,
        "topic": topic,
        "difficulty": difficulty
    })

@router.post("/submit_quiz")
async def submit_quiz(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/auth/login")

    form = await request.form()
    answers = {}
    for key, value in form.items():
        if key.startswith("answer_"):
            qnum = key.split("_")[1]
            answers[qnum] = value.strip()

    quiz = request.session.get("last_quiz")
    topic = request.session.get("last_quiz_topic", "Unknown Topic")
    difficulty = request.session.get("last_quiz_difficulty", "medium")

    if not quiz:
        return RedirectResponse(url="/student/dashboard")

    total = len(quiz)
    score = 0
    results = []

    for i, q in enumerate(quiz, start=1):
        qid = str(i)
        correct_answer = q.get("answer")
        student_answer = answers.get(qid, None)
        is_correct = (student_answer == correct_answer)
        if is_correct:
            score += 1
        results.append({
            "question": q["question"],
            "correct_answer": correct_answer,
            "student_answer": student_answer,
            "is_correct": is_correct,
            "explanation": f"The correct answer is {correct_answer}."
        })

    # Save result to Pinecone DB
    save_quiz_result(
        student_email=user.get("email"),
        topic=topic,
        difficulty=difficulty,
        score=score,
        results=results
    )

    return templates.TemplateResponse("quiz_results.html", {
        "request": request,
        "results": results,
        "score": score,
        "total": total,
        "topic": topic,
        "difficulty": difficulty
    })

@router.get("/educator/results/{course_name}")
async def educator_results(request: Request, course_name: str):
    user = request.session.get("user")
    if not user or user.get("role") != "educator":
        return RedirectResponse(url="/auth/login")

    # Query Pinecone for all results for this course
    from app.core.pinecone_client import query_pinecone
    matches = query_pinecone(
        query_vector=[0.0]*1536,
        top_k=100,
        filter={"course_name": course_name}
    )

    # Parse results JSON
    all_results = []
    for match in matches:
        meta = match.metadata
        try:
            meta["results"] = json.loads(meta.get("results_json", "[]"))
        except Exception:
            meta["results"] = []
        all_results.append(meta)

    return templates.TemplateResponse("educator_results.html", {
        "request": request,
        "results": all_results,
        "course_name": course_name
    })