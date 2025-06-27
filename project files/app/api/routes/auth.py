from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.oauth import get_auth_flow, fetch_user_info, fetch_courses

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login")
def login():
    flow = get_auth_flow()
    auth_url, _ = flow.authorization_url(prompt='consent')
    return RedirectResponse(auth_url)

@router.get("/callback")
async def callback(request: Request):
    flow = get_auth_flow()
    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials
    user_info = fetch_user_info(credentials)

    # Store user info in session (ensure SessionMiddleware is set up)
    request.session["user"] = user_info

    # Redirect to role selection or dashboard page
    return RedirectResponse(url="/auth/role_selection", status_code=303)

@router.get("/role_selection")
async def role_selection(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/auth/login")

    return templates.TemplateResponse("login_role_selection.html", {
        "request": request,
        "user_email": user["email"],
        "user_name": user["name"]
    })

@router.post("/set_role")
async def set_role(request: Request, role: str = Form(...), email: str = Form(...)):
    request.session["role"] = role
    if role == "student":
        return RedirectResponse(url="/student/dashboard", status_code=303)
    return RedirectResponse(url="/educator/dashboard", status_code=303)
@router.get("/logout")
def logout():
    return templates.TemplateResponse("logged_out.html", {"request": {}})
