"""
NutriBot AI Agent — powered by IBM WatsonX.ai Granite models.
Provides customized nutrition and diet plans via natural language.
"""

import os
from dotenv import load_dotenv
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

load_dotenv()


# ──────────────────────────────────────────────
#  WatsonX client singleton
# ──────────────────────────────────────────────

def _build_client() -> APIClient:
    creds = Credentials(
        url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
        api_key=os.getenv("WATSONX_API_KEY"),
    )
    return APIClient(creds)


def _get_model(model_id: str | None = None) -> ModelInference:
    client = _build_client()
    chosen_model = model_id or os.getenv(
        "GRANITE_CHAT_MODEL_ID", "ibm/granite-3-8b-instruct"
    )
    params = {
        GenParams.MAX_NEW_TOKENS: 1024,
        GenParams.MIN_NEW_TOKENS: 50,
        GenParams.TEMPERATURE: 0.7,
        GenParams.TOP_P: 0.9,
        GenParams.REPETITION_PENALTY: 1.1,
    }
    return ModelInference(
        model_id=chosen_model,
        params=params,
        credentials=Credentials(
            url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
            api_key=os.getenv("WATSONX_API_KEY"),
        ),
        project_id=os.getenv("WATSONX_PROJECT_ID"),
    )


# ──────────────────────────────────────────────
#  Prompt builders
# ──────────────────────────────────────────────

SYSTEM_PERSONA = """You are NutriBot, a certified AI nutrition specialist and dietitian assistant.
You create personalized, science-based nutrition and diet plans.
Always consider age, weight, height, activity level, health goals, dietary restrictions, and medical conditions.
Provide practical, culturally sensitive, and sustainable dietary advice.
Include specific foods, portions, macros, and timing when giving meal plans.
Always recommend consulting a healthcare professional for medical conditions."""


def _build_nutrition_plan_prompt(profile: dict) -> str:
    return f"""{SYSTEM_PERSONA}

Create a comprehensive 7-day personalized nutrition and diet plan for the following profile:

Name: {profile.get('name', 'User')}
Age: {profile.get('age', 'N/A')} years
Gender: {profile.get('gender', 'N/A')}
Weight: {profile.get('weight', 'N/A')} kg
Height: {profile.get('height', 'N/A')} cm
BMI: {profile.get('bmi', 'N/A')}
Activity Level: {profile.get('activity_level', 'Moderate')}
Health Goal: {profile.get('goal', 'Maintain healthy weight')}
Dietary Restrictions: {profile.get('restrictions', 'None')}
Medical Conditions: {profile.get('medical_conditions', 'None')}
Allergies: {profile.get('allergies', 'None')}
Food Preferences: {profile.get('preferences', 'No specific preferences')}

Please provide:
1. Daily caloric target and macronutrient breakdown (proteins, carbs, fats)
2. A complete 7-day meal plan with breakfast, lunch, dinner, and 2 snacks each day
3. Portion sizes and key nutrients for each meal
4. Hydration guidelines
5. Supplement recommendations if applicable
6. Foods to avoid
7. Weekly shopping list summary
8. Tips for meal prep and sustainability

Nutrition Plan:"""


def _build_meal_prompt(meal_request: dict) -> str:
    return f"""{SYSTEM_PERSONA}

Generate a detailed meal plan based on these requirements:

Meal Type: {meal_request.get('meal_type', 'Full day')}
Cuisine Preference: {meal_request.get('cuisine', 'Any')}
Caloric Target: {meal_request.get('calories', 2000)} kcal/day
Dietary Style: {meal_request.get('diet_style', 'Balanced')}
Preparation Time Available: {meal_request.get('prep_time', '30 minutes')}
Number of People: {meal_request.get('servings', 1)}
Special Requirements: {meal_request.get('special_req', 'None')}

Provide:
- Recipe names with ingredients and quantities
- Macronutrient breakdown per meal
- Preparation instructions (concise)
- Estimated cost per serving

Meal Plan:"""


def _build_chat_prompt(user_message: str, history: list[dict]) -> str:
    convo = "\n".join(
        f"{'User' if m['role'] == 'user' else 'NutriBot'}: {m['content']}"
        for m in history[-6:]  # last 6 turns for context
    )
    return f"""{SYSTEM_PERSONA}

Previous conversation:
{convo}

User: {user_message}
NutriBot:"""


def _build_bmi_advice_prompt(bmi_data: dict) -> str:
    return f"""{SYSTEM_PERSONA}

Provide personalized health and nutrition advice based on this BMI assessment:

Name: {bmi_data.get('name', 'User')}
Age: {bmi_data.get('age', 'N/A')}
Gender: {bmi_data.get('gender', 'N/A')}
BMI: {bmi_data.get('bmi', 'N/A')}
BMI Category: {bmi_data.get('category', 'N/A')}
Weight: {bmi_data.get('weight', 'N/A')} kg
Height: {bmi_data.get('height', 'N/A')} cm

Provide:
1. What this BMI means for their health
2. Specific dietary recommendations to reach a healthy BMI
3. Recommended daily caloric intake
4. Key nutrients to focus on
5. Foods to prioritize and avoid
6. Realistic timeline expectations
7. Lifestyle tips beyond diet

BMI Health Advice:"""


def _build_family_plan_prompt(family: list[dict]) -> str:
    members = "\n".join(
        f"  - {m.get('name')}: Age {m.get('age')}, Gender {m.get('gender')}, "
        f"Goal: {m.get('goal', 'General health')}, "
        f"Restrictions: {m.get('restrictions', 'None')}"
        for m in family
    )
    return f"""{SYSTEM_PERSONA}

Create a unified family nutrition plan that meets everyone's needs:

Family Members:
{members}

Provide:
1. A shared family meal plan that works for all members
2. Individual modifications for each member where needed
3. Kid-friendly adaptations (if children present)
4. Budget-conscious shopping strategy
5. Batch cooking tips for the whole family
6. Nutritional highlights that benefit all ages

Family Nutrition Plan:"""


# ──────────────────────────────────────────────
#  Public API functions
# ──────────────────────────────────────────────

def generate_nutrition_plan(profile: dict) -> str:
    """Generate a full 7-day personalized nutrition plan."""
    model = _get_model()
    prompt = _build_nutrition_plan_prompt(profile)
    response = model.generate_text(prompt=prompt)
    return response.strip() if isinstance(response, str) else response


def generate_meal_plan(meal_request: dict) -> str:
    """Generate a specific meal plan based on user requirements."""
    model = _get_model()
    prompt = _build_meal_prompt(meal_request)
    response = model.generate_text(prompt=prompt)
    return response.strip() if isinstance(response, str) else response


def chat_with_nutritionist(user_message: str, history: list[dict] | None = None) -> str:
    """Conversational AI nutritionist chat."""
    model = _get_model()
    prompt = _build_chat_prompt(user_message, history or [])
    response = model.generate_text(prompt=prompt)
    return response.strip() if isinstance(response, str) else response


def get_bmi_advice(bmi_data: dict) -> str:
    """Get AI-powered nutrition advice based on BMI data."""
    model = _get_model()
    prompt = _build_bmi_advice_prompt(bmi_data)
    response = model.generate_text(prompt=prompt)
    return response.strip() if isinstance(response, str) else response


def generate_family_plan(family_members: list[dict]) -> str:
    """Generate a unified nutrition plan for a whole family."""
    model = _get_model()
    prompt = _build_family_plan_prompt(family_members)
    response = model.generate_text(prompt=prompt)
    return response.strip() if isinstance(response, str) else response


# ──────────────────────────────────────────────
#  BMI calculation helper
# ──────────────────────────────────────────────

def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    """Calculate BMI and return category with health info."""
    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError("Weight and height must be positive numbers.")
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 1)

    if bmi < 18.5:
        category = "Underweight"
        color = "#3b82f6"
        description = "Below healthy weight range — focus on nutrient-dense caloric intake."
    elif bmi < 25:
        category = "Normal weight"
        color = "#22c55e"
        description = "Healthy weight range — maintain balanced nutrition."
    elif bmi < 30:
        category = "Overweight"
        color = "#f59e0b"
        description = "Above healthy range — moderate caloric reduction and activity increase recommended."
    else:
        category = "Obese"
        color = "#ef4444"
        description = "Significant health risks — consult a healthcare provider and registered dietitian."

    # Ideal weight range using BMI 18.5–24.9
    height_m2 = height_m ** 2
    ideal_min = round(18.5 * height_m2, 1)
    ideal_max = round(24.9 * height_m2, 1)

    return {
        "bmi": bmi,
        "category": category,
        "color": color,
        "description": description,
        "ideal_weight_min": ideal_min,
        "ideal_weight_max": ideal_max,
    }


def calculate_tdee(profile: dict) -> dict:
    """Calculate Total Daily Energy Expenditure using Mifflin-St Jeor equation."""
    weight = profile.get("weight", 70)
    height = profile.get("height", 170)
    age = profile.get("age", 30)
    gender = profile.get("gender", "male").lower()
    activity = profile.get("activity_level", "moderate").lower()

    # Mifflin-St Jeor BMR
    if gender == "female":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5

    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very active": 1.9,
    }
    multiplier = activity_multipliers.get(activity, 1.55)
    tdee = round(bmr * multiplier)

    return {
        "bmr": round(bmr),
        "tdee": tdee,
        "weight_loss": tdee - 500,
        "weight_gain": tdee + 500,
        "macros": {
            "protein_g": round(weight * 1.6),
            "carbs_g": round((tdee * 0.45) / 4),
            "fat_g": round((tdee * 0.30) / 9),
        },
    }
