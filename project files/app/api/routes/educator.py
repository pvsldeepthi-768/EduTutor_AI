from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.pinecone_client import query_pinecone

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
async def educator_dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/auth/login")
    
    # Fetch performance insights from Pinecone vector DB
    insights = query_pinecone()  # Implement this in pinecone_client.py
    
    # You can fetch quiz history from your DB or mock data for now
    quiz_history = [
        {"student": "Alice", "score": 85, "last_topic": "Photosynthesis"},
        {"student": "Bob", "score": 78, "last_topic": "Cell Structure"},
    ]
    
    return templates.TemplateResponse("educator_dashboard.html", {
        "request": request,
        "user": user,
        "insights": insights,
        "quiz_history": quiz_history
    })
