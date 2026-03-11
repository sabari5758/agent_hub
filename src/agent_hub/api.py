import os

from fastapi import FastAPI, HTTPException
from agent_hub.crew import AgentHub
from agent_hub.schema import TrendRequest, TrendResult, JobResult
from crewai import Crew

app = FastAPI(title="IT Sector Agent API")
tracker = AgentHub()

# ENDPOINT 1: Only runs the Tech Scout / Research
@app.post("/research", response_model=TrendResult)
async def get_tech_trends(payload: TrendRequest):
    try:
        # Create a temporary crew to run just the research task
        # We must manually assign the agent to the task for this isolated execution
        agent = tracker.tech_scout()
        task = tracker.research_task()
        task.agent = agent
        
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )

        result = crew.kickoff(inputs={
            "topic": payload.topic,
            "platform": payload.platform 
        })
        
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
@app.post("/career-advice", response_model=JobResult)
async def get_career_advice(payload: TrendRequest):
    try:
        agent = tracker.career_analyst()
        task = tracker.analysis_task()
        task.agent = agent

        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )

        result = crew.kickoff(inputs={
            "topic": payload.topic,
            "platform": payload.platform 
        })
        
        raw_data = []
        topic_result = payload.topic

        if result.pydantic and hasattr(result.pydantic, 'jobs'):
            print(f"DEBUG: Pydantic Output: {result.pydantic}")
            raw_data = [t.model_dump() if hasattr(t, 'model_dump') else t for t in result.pydantic.jobs]
            if hasattr(result.pydantic, 'topic'):
                topic_result = result.pydantic.topic
        elif result.json_dict:
            print(f"DEBUG: Raw Agent Output: {result.raw}")
            raw_data = result.json_dict.get('jobs', [])
            topic_result = result.json_dict.get('topic', payload.topic)
        
        return {"jobs": raw_data, "topic": topic_result, "status": "completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Render and other servers provide a "PORT" environment variable
    port = int(os.environ.get("PORT", 8000)) 
    
    # Use 0.0.0.0 to make it accessible to the outside world
    uvicorn.run("main:app", host="0.0.0.0", port=port)
