"""
NutriBot FastAPI Backend
Serves all API endpoints for the nutrition AI agent.
"""

import os
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from nutrition_agent import (
    generate_nutrition_plan,
    generate_meal_plan,
    chat_with_nutritionist,
    get_bmi_advice,
    generate_family_plan,
    calculate_bmi,
    calculate_tdee,
)

load_dotenv()

app = FastAPI(
    title="NutriBot AI",
    description="AI-powered nutrition and diet planning using IBM WatsonX.ai Granite models",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend files
static_dir = Path("frontend")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# ──────────────────────────────────────────────
#  Pydantic models
# ──────────────────────────────────────────────

class UserProfile(BaseModel):
    name: str = "User"
    age: int = Field(ge=1, le=120)
    gender: str
    weight: float = Field(gt=0, description="Weight in kg")
    height: float = Field(gt=0, description="Height in cm")
    activity_level: str = "moderate"
    goal: str = "Maintain healthy weight"
    restrictions: str = "None"
    medical_conditions: str = "None"
    allergies: str = "None"
    preferences: str = "No specific preferences"


class MealRequest(BaseModel):
    meal_type: str = "Full day"
    cuisine: str = "Any"
    calories: int = Field(default=2000, ge=800, le=5000)
    diet_style: str = "Balanced"
    prep_time: str = "30 minutes"
    servings: int = Field(default=1, ge=1, le=20)
    special_req: str = "None"


class ChatMessage(BaseModel):
    message: str
    history: list[dict] = []


class BMIRequest(BaseModel):
    weight: float = Field(gt=0)
    height: float = Field(gt=0)
    name: str = "User"
    age: int = Field(default=30, ge=1, le=120)
    gender: str = "male"


class FamilyMember(BaseModel):
    name: str
    age: int
    gender: str
    weight: float
    height: float
    goal: str = "General health"
    restrictions: str = "None"


class FamilyPlanRequest(BaseModel):
    members: list[FamilyMember]


# ──────────────────────────────────────────────
#  Routes — Pages
# ──────────────────────────────────────────────

@app.get("/")
async def serve_index():
    return FileResponse("frontend/index.html")


@app.get("/meal-planning")
async def serve_meal_planning():
    return FileResponse("frontend/meal_planning.html")


@app.get("/bmi-calculator")
async def serve_bmi():
    return FileResponse("frontend/bmi_calculator.html")


@app.get("/family-profiles")
async def serve_family():
    return FileResponse("frontend/family_profiles.html")


@app.get("/ai-agent")
async def serve_agent():
    return FileResponse("frontend/ai_agent.html")


# ──────────────────────────────────────────────
#  Routes — API
# ──────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "NutriBot AI",
        "model": os.getenv("GRANITE_CHAT_MODEL_ID", "ibm/granite-3-8b-instruct"),
    }


@app.post("/api/nutrition-plan")
async def api_nutrition_plan(profile: UserProfile):
    """Generate a personalized 7-day nutrition plan."""
    try:
        bmi_info = calculate_bmi(profile.weight, profile.height)
        tdee_info = calculate_tdee(profile.model_dump())
        enriched = profile.model_dump()
        enriched["bmi"] = bmi_info["bmi"]
        enriched["bmi_category"] = bmi_info["category"]
        enriched["tdee"] = tdee_info["tdee"]
        plan = generate_nutrition_plan(enriched)
        return {
            "success": True,
            "plan": plan,
            "bmi": bmi_info,
            "tdee": tdee_info,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/meal-plan")
async def api_meal_plan(request: MealRequest):
    """Generate a specific meal plan."""
    try:
        plan = generate_meal_plan(request.model_dump())
        return {"success": True, "meal_plan": plan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def api_chat(msg: ChatMessage):
    """Chat with the AI nutritionist."""
    try:
        reply = chat_with_nutritionist(msg.message, msg.history)
        return {"success": True, "reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bmi")
async def api_bmi(req: BMIRequest):
    """Calculate BMI and get AI-powered advice."""
    try:
        bmi_info = calculate_bmi(req.weight, req.height)
        bmi_data = {**bmi_info, "name": req.name, "age": req.age,
                    "gender": req.gender, "weight": req.weight, "height": req.height}
        advice = get_bmi_advice(bmi_data)
        return {"success": True, "bmi": bmi_info, "advice": advice}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bmi/calculate-only")
async def api_bmi_only(req: BMIRequest):
    """Calculate BMI without AI advice (instant)."""
    try:
        bmi_info = calculate_bmi(req.weight, req.height)
        tdee_info = calculate_tdee(req.model_dump())
        return {"success": True, "bmi": bmi_info, "tdee": tdee_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/family-plan")
async def api_family_plan(request: FamilyPlanRequest):
    """Generate a unified family nutrition plan."""
    try:
        members_data = []
        for m in request.members:
            md = m.model_dump()
            bmi_info = calculate_bmi(m.weight, m.height)
            md["bmi"] = bmi_info["bmi"]
            md["bmi_category"] = bmi_info["category"]
            members_data.append(md)
        plan = generate_family_plan(members_data)
        return {"success": True, "family_plan": plan, "members_bmi": members_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tdee")
async def api_tdee(profile: UserProfile):
    """Calculate TDEE and macros."""
    try:
        tdee_info = calculate_tdee(profile.model_dump())
        return {"success": True, "tdee": tdee_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=os.getenv("DEBUG", "True").lower() == "true",
    )
