from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI
from agent.giggenie_agent import GigGenieAgent

app = FastAPI(title="GigGenie")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/app")
def frontend():
    return FileResponse("frontend/index.html")

agent = GigGenieAgent()


@app.get("/")
def home():
    return {
        "message": "GigGenie is alive! 🚀",
        "status": "running"
    }


@app.post("/analyze-profile")
def analyze_profile(profile: dict):
    return agent.analyze_profile(profile)


@app.post("/find-opportunities")
def find_opportunities(profile: dict):
    opportunities = agent.find_opportunities(profile)
    action_plan = agent.create_action_plan(profile, opportunities)

    return {
        "agent": "GigGenie",
        "profile": profile,
        "opportunities_found": len(opportunities),
        "matches": opportunities,
        "action_plan": action_plan
    }