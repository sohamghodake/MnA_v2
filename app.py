import io
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn

from src.reasoning.orchestrator import ReasoningOrchestrator
from src.reasoning.strategy import StrategyInput
from src.output.generator import ReportGenerator

app = FastAPI(
    title="M&A Deal Intelligence API",
    description="AI-Powered M&A Analysis Platform with strict Ontology and Knowledge Graph integration.",
    version="2.0.0"
)

# ── Request/Response Models ──────────────────────────────────────────────────

class AnalysisRequest(BaseModel):
    query: str
    objective: str = "Vertical Integration"
    horizon: int = 12
    risk: str = "medium"
    deal_type: str = "acquisition"        # "merger" | "acquisition"
    company_a_name: Optional[str] = "Company A"
    company_b_name: Optional[str] = "Company B"
    company_a_role: Optional[str] = "Acquirer"
    company_b_role: Optional[str] = "Acquiree"
    company_a_text: Optional[str] = ""
    company_b_text: Optional[str] = ""


class AnalysisResponse(BaseModel):
    status: str
    reports: Dict[str, str]               # report_key -> formatted markdown
    objective: str
    time_horizon_months: int
    deal_type: str


class UploadResponse(BaseModel):
    company: str
    filename: str
    extracted_text: str
    char_count: int


# ── Helper: extract text from PDF or plain file ───────────────────────────────

def extract_text_from_upload(file_bytes: bytes, filename: str) -> str:
    """Extracts text from a PDF or plain text file."""
    if filename.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            return "\n".join(
                page.extract_text() or "" for page in reader.pages
            ).strip()
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"PDF parsing failed: {e}")
    else:
        # Plain text / docx fallback: decode as utf-8
        try:
            return file_bytes.decode("utf-8", errors="replace").strip()
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"File decoding failed: {e}")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/api/status")
def read_status():
    return {"message": "M&A Analysis Platform API is running.", "version": "2.0.0"}


@app.post("/api/upload-docs", response_model=UploadResponse)
async def upload_document(
    company: str = Form(...),         # "a" or "b"
    file: UploadFile = File(...),
):
    """Upload and extract text from a company document (PDF or TXT)."""
    file_bytes = await file.read()
    extracted = extract_text_from_upload(file_bytes, file.filename or "upload.txt")
    return UploadResponse(
        company=company,
        filename=file.filename or "upload",
        extracted_text=extracted,
        char_count=len(extracted),
    )


@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze_deal(request: AnalysisRequest):
    strategy = StrategyInput(
        objective=request.objective,
        time_horizon_months=request.horizon,
        risk_tolerance=request.risk,
    )

    orchestrator = None
    try:
        orchestrator = ReasoningOrchestrator()

        # Generate all four reports
        raw_reports = orchestrator.generate_reports(
            strategy=strategy,
            user_query=request.query,
            deal_type=request.deal_type,
            company_a_name=request.company_a_name or "Company A",
            company_b_name=request.company_b_name or "Company B",
            company_a_role=request.company_a_role or "Acquirer",
            company_b_role=request.company_b_role or "Acquiree",
            company_a_text=request.company_a_text or "",
            company_b_text=request.company_b_text or "",
        )

        # Format reports
        generator = ReportGenerator()
        formatted_reports = generator.format_to_markdown(
            reports=raw_reports,
            strategy=strategy,
            validation_status=True,
            deal_type=request.deal_type,
            company_a_name=request.company_a_name or "Company A",
            company_b_name=request.company_b_name or "Company B",
        )

        return AnalysisResponse(
            status="success",
            reports=formatted_reports,
            objective=strategy.objective,
            time_horizon_months=strategy.time_horizon_months,
            deal_type=request.deal_type,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if orchestrator:
            orchestrator.close()


# Mount static files (must be after API routes)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
