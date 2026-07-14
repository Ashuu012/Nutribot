# 🌿 NutriBot AI — Nutrition Agent with IBM WatsonX.ai

> A full-stack AI-powered nutrition and diet planning application using **IBM WatsonX.ai Granite models**, **FastAPI**, and a modern HTML/CSS/JS frontend.

---

## 📁 Project Structure

```
nutribot/
├── .env                    # IBM WatsonX.ai credentials (NEVER commit this)
├── requirements.txt        # Python dependencies
├── nutrition_agent.py      # IBM Granite AI agent — prompts + business logic
├── app.py                  # FastAPI backend + all REST API endpoints
├── frontend/
│   ├── index.html          # Nutrition Dashboard
│   ├── meal_planning.html  # AI Meal Planner
│   ├── bmi_calculator.html # BMI Calculator + AI Advice
│   ├── family_profiles.html# Family Profile Manager
│   └── ai_agent.html       # AI Nutritionist Chat Interface
└── README.md               # This file
```

---

## 🔑 Prerequisites

- Python 3.10 or higher
- IBM Cloud account with WatsonX.ai access
- IBM WatsonX.ai Project ID

---

## 🚀 Step 1 — IBM WatsonX.ai Setup

### 1.1 Get your IBM Cloud API Key
1. Go to [https://cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys)
2. Click **Create an IBM Cloud API key**
3. Copy the key — you only see it once

### 1.2 Get your WatsonX Project ID
1. Go to [https://dataplatform.cloud.ibm.com/wx/home](https://dataplatform.cloud.ibm.com/wx/home)
2. Open or create a WatsonX project
3. Go to **Manage** → **General** → copy the **Project ID**

### 1.3 Configure your `.env` file
Edit `.env` with your real credentials:
```env
WATSONX_API_KEY=your_actual_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_actual_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
GRANITE_CHAT_MODEL_ID=ibm/granite-3-8b-instruct
```

> ⚠️ **Never commit `.env` to version control.** It's in `.gitignore` by default.

---

## ⚙️ Step 2 — Local Installation

### 2.1 Activate virtual environment
```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

### 2.2 Install dependencies
```bash
pip install -r requirements.txt
```

---

## ▶️ Step 3 — Run the Application

```bash
python app.py
```

The server starts at: **http://localhost:8000**

| Page | URL |
|------|-----|
| 🌿 Dashboard | http://localhost:8000/ |
| 🍽️ Meal Planning | http://localhost:8000/meal-planning |
| ⚖️ BMI Calculator | http://localhost:8000/bmi-calculator |
| 👨‍👩‍👧‍👦 Family Profiles | http://localhost:8000/family-profiles |
| 🤖 AI Agent | http://localhost:8000/ai-agent |
| 📚 API Docs | http://localhost:8000/docs |

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/nutrition-plan` | Generate 7-day nutrition plan |
| POST | `/api/meal-plan` | Generate custom meal plan |
| POST | `/api/chat` | Chat with AI nutritionist |
| POST | `/api/bmi` | BMI calculation + AI advice |
| POST | `/api/bmi/calculate-only` | BMI + TDEE (no AI, instant) |
| POST | `/api/family-plan` | Family nutrition plan |
| POST | `/api/tdee` | Calculate TDEE + macros |

---

## 🧠 AI Model Configuration

The agent uses **IBM Granite 3.8B Instruct** by default. You can switch models in `.env`:

| Model ID | Description |
|----------|-------------|
| `ibm/granite-3-8b-instruct` | Fast, accurate (recommended) |
| `ibm/granite-13b-instruct-v2` | Larger, more detailed |
| `ibm/granite-3-2b-instruct` | Lightweight, fastest |

---

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
```

### Build & run
```bash
docker build -t nutribot-ai .
docker run -p 8000:8000 --env-file .env nutribot-ai
```

---

## ☁️ Cloud Deployment

### IBM Code Engine (recommended)
```bash
# Install IBM Cloud CLI first
ibmcloud login
ibmcloud ce project create --name nutribot
ibmcloud ce application create \
  --name nutribot-app \
  --image us.icr.io/your-namespace/nutribot-ai \
  --port 8000 \
  --env-from-secret nutribot-secrets
```

### Heroku
```bash
heroku create nutribot-ai-app
heroku config:set WATSONX_API_KEY=your_key
heroku config:set WATSONX_PROJECT_ID=your_project_id
heroku config:set WATSONX_URL=https://us-south.ml.cloud.ibm.com
git push heroku main
```

### Railway / Render
1. Connect your GitHub repository
2. Set environment variables in the dashboard
3. Set start command: `python app.py`
4. Deploy — Railway/Render auto-detects Python

---

## 🩺 Features Overview

| Feature | Description |
|---------|-------------|
| **Nutrition Dashboard** | Quick plan generator with BMI/TDEE display |
| **Meal Planning** | Cuisine-aware, diet-style meal plans (keto, vegan, Mediterranean, etc.) |
| **BMI Calculator** | Visual BMI gauge with AI-powered health advice |
| **Family Profiles** | Manage multiple profiles, unified family nutrition plan |
| **AI Chat Agent** | Full conversational AI nutritionist with quick commands |

---

## 🔧 Troubleshooting

**`AuthenticationError`**: Check that `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` are set correctly in `.env`.

**`ModelNotFound`**: Ensure the Granite model is available in your WatsonX region. Try `ibm/granite-3-8b-instruct`.

**`CORS error` in browser**: The FastAPI backend already includes CORS middleware for all origins.

**Port already in use**: Change `APP_PORT` in `.env` or kill the existing process.

---

## 📄 License

MIT License — Built with ❤️ using IBM WatsonX.ai + Granite models.

---

> 🌿 **Disclaimer**: NutriBot AI provides general nutrition information. Always consult a registered dietitian or healthcare professional for medical dietary advice.
