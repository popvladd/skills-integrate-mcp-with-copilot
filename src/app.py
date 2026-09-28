"""
High School Management System API

A super simple FastAPI application that allows students to view activities and
teachers to manage extracurricular enrollment at Mergington High School.
"""

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
import secrets
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET") or secrets.token_urlsafe(32),
    max_age=8 * 60 * 60,
    same_site="strict",
    https_only=os.environ.get("SESSION_COOKIE_SECURE", "").lower() == "true",
)

TEACHER_USERNAME = os.environ.get("TEACHER_USERNAME")
TEACHER_PASSWORD = os.environ.get("TEACHER_PASSWORD")


class LoginRequest(BaseModel):
    username: str
    password: str

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/auth/login")
def login(credentials: LoginRequest, request: Request):
    username_matches = secrets.compare_digest(
        credentials.username.encode("utf-8"), (TEACHER_USERNAME or "").encode("utf-8")
    )
    password_matches = secrets.compare_digest(
        credentials.password.encode("utf-8"), (TEACHER_PASSWORD or "").encode("utf-8")
    )
    if not TEACHER_USERNAME or not TEACHER_PASSWORD or not (
        username_matches and password_matches
    ):
        raise HTTPException(status_code=401, detail="Invalid teacher credentials")

    csrf_token = secrets.token_urlsafe(32)
    request.session.clear()
    request.session["teacher"] = TEACHER_USERNAME
    request.session["csrf_token"] = csrf_token
    return {"authenticated": True, "csrf_token": csrf_token}


@app.get("/auth/session")
def get_session(request: Request):
    teacher = request.session.get("teacher")
    if not teacher:
        return {"authenticated": False}
    return {
        "authenticated": True,
        "csrf_token": request.session.get("csrf_token"),
    }


def require_teacher(
    request: Request,
    csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
):
    expected_token = request.session.get("csrf_token")
    if not request.session.get("teacher") or not expected_token:
        raise HTTPException(status_code=401, detail="Teacher login required")
    if not csrf_token or not secrets.compare_digest(
        csrf_token.encode("utf-8"), expected_token.encode("utf-8")
    ):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")


@app.post("/auth/logout", dependencies=[Depends(require_teacher)])
def logout(request: Request):
    request.session.clear()
    return {"authenticated": False}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(
    activity_name: str,
    email: str,
    _: None = Depends(require_teacher),
):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(
    activity_name: str,
    email: str,
    _: None = Depends(require_teacher),
):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
