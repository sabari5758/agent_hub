from fastapi import FastAPI
from pydantic import BaseModel
from agent_hub.crew import AgentHub

app = FastAPI()

class CrewInput(BaseModel):
    topic: str

from fastapi import FastAPI, HTTPException
from agent_hub.crew import AgentHub
from agent_hub.schema import TrendRequest, TrendResponse

app = FastAPI(title="IT Sector Agent API")
tracker = AgentHub()

# ENDPOINT 1: Only runs the Tech Scout / Research
@app.post("/research", response_model=TrendResponse)
async def get_tech_trends(payload: TrendRequest):
    try:
        # We manually trigger just the research task
        inputs =  payload.topic
    
        
        # Logic: Use the specific task/agent without running the whole crew
        # Note: 'research_task' must be defined in your CrewBase class
        result = tracker.research_task().execute_sync(context=inputs)
        print(f"DEBUG: Raw Agent Output: {result.raw}")
        # 2. Extract raw data safely
        # If result.pydantic exists, convert it to a dict first
        raw_data = []
        if result.pydantic and hasattr(result.pydantic, 'trends'):
            raw_data = [t.model_dump() if hasattr(t, 'model_dump') else t for t in result.pydantic.trends]
        elif result.json_dict:
            raw_data = result.json_dict.get('trends', [])

        return {
            "trends": raw_data,
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ENDPOINT 2: Only runs the Career Analyst
@app.post("/career-advice")
async def get_career_advice(payload: TrendRequest):
    # This endpoint could take the output of Endpoint 1 as input
    try:
        result = tracker.analysis_task().execute_sync(context=payload.topic)
        
        raw_data = []
        if result.pydantic and hasattr(result.pydantic, 'jobs'):
            print(f"DEBUG: Pydantic Output: {result.pydantic}")
            raw_data = [t.model_dump() if hasattr(t, 'model_dump') else t for t in result.pydantic.jobs]
        elif result.json_dict:
            print(f"DEBUG: Raw Agent Output: {result.raw}")
            raw_data = result.json_dict.get('jobs', [])
        
        return {"advice": raw_data, "status": "completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
