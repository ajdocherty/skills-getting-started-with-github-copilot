"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Basketball": {
        "description": "Team basketball practice and games",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["james@mergington.edu"]
        },
        "Soccer": {
        "description": "Competitive soccer training and matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["alex@mergington.edu"]
        },
        "Debate Club": {
        "description": "Develop public speaking and critical thinking skills",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["sarah@mergington.edu", "marcus@mergington.edu"]
        },
        "Robotics Club": {
        "description": "Design and build robots for competitions",
        "schedule": "Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 14,
        "participants": ["lucas@mergington.edu"]
        },
        "Art Studio": {
        "description": "Painting, drawing, and sculpture techniques",
        "schedule": "Mondays and Fridays, 3:30 PM - 4:45 PM",
        "max_participants": 20,
        "participants": ["isabella@mergington.edu", "grace@mergington.edu"]
        },
        "Music Band": {
        "description": "Learn instruments and perform in school concerts",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
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
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


# API endpoints for frontend compatibility
@app.get("/api/activities")
def api_get_activities():
    # return activities as list of objects with id and name
    result = []
    for name, info in activities.items():
        result.append({
            "id": name,
            "name": name,
            "description": info.get("description", "")
        })
    return result


@app.get("/api/signups")
def api_get_signups():
    # return list of { activityId, email }
    out = []
    for name, info in activities.items():
        for email in info.get("participants", []):
            out.append({"activityId": name, "email": email})
    return out


@app.post("/api/signups")
async def api_post_signup(req: Request):
    payload = await req.json()
    email = payload.get("email")
    activityId = payload.get("activityId")
    if not activityId or not email:
        raise HTTPException(status_code=400, detail="email and activityId required")
    if activityId not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    if email in activities[activityId]["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")
    activities[activityId]["participants"].append(email)
    return {"message": f"Signed up {email} for {activityId}"}


@app.delete("/api/signups")
async def api_delete_signup(req: Request):
    # accept JSON body { email, activityId }
    payload = await req.json()
    email = payload.get("email")
    activityId = payload.get("activityId")
    if not activityId or not email:
        raise HTTPException(status_code=400, detail="email and activityId required")
    if activityId not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    try:
        activities[activityId]["participants"].remove(email)
    except ValueError:
        raise HTTPException(status_code=404, detail="Signup not found")
    return {"message": f"Removed {email} from {activityId}"}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Check if already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")
    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}
