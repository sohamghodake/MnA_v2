from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import uvicorn

from src.reasoning.orchestrator import ReasoningOrchestrator
from src.reasoning.strategy import StrategyInput
from src.output.generator import ReportGenerator

app = FastAPI(
    title="M&A Deal Intelligence API",
    description="AI-Powered M&A Analysis Platform with strict Ontology and Knowledge Graph integration.",
    version="1.0.0"
)

# Request Models
class AnalysisRequest(BaseModel):
    query: str
    objective: str = "Acquisition"
    horizon: int = 12
    risk: str = "medium"

# Response Models
class AnalysisResponse(BaseModel):
    status: str
    markdown_report: str
    objective: str
    time_horizon_months: int

@app.get("/api/status")
def read_status():
    return {"message": "M&A Analysis Platform API is running."}

@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze_deal(request: AnalysisRequest):
    # 1. Setup Strategy
    strategy = StrategyInput(
        objective=request.objective,
        time_horizon_months=request.horizon,
        risk_tolerance=request.risk
    )
    
    orchestrator = None
    try:
        # 2. Initialize Orchestrator
        orchestrator = ReasoningOrchestrator()
        
        # 3. Generate content
        content = orchestrator.generate_report(strategy, request.query)
        
        # 4. Format Output
        generator = ReportGenerator()
        is_valid = "Validation Failed" not in content
        final_report = generator.format_to_markdown(content, strategy, is_valid)
        
        return AnalysisResponse(
            status="success" if is_valid else "validation_failed",
            markdown_report=final_report,
            objective=strategy.objective,
            time_horizon_months=strategy.time_horizon_months
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if orchestrator:
            orchestrator.close()

# Mount the static files directory to serve the frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
