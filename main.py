"""FastAPI application for Job Scraper with Rate Limiting."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from serp_client import search_jobs
from groq_client import summarize_job

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Job Scraper API",
    description="Search and analyze job listings using SERP API and Groq AI",
    version="1.0.0"
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


class JobSearchRequest(BaseModel):
    """Request model for job search."""
    query: str
    location: str
    num_jobs: Optional[int] = 20
    remote_only: Optional[bool] = False


class SummarizeRequest(BaseModel):
    """Request model for job summarization."""
    description: str


@app.get("/")
async def serve_frontend():
    """Serve the main frontend page."""
    return FileResponse("static/index.html")


@app.post("/api/search")
@limiter.limit("4/minute")
async def search_jobs_endpoint(request: Request, body: JobSearchRequest):
    """
    Search for jobs using SERP API.
    Rate limited to 4 requests per minute per IP.
    
    - **query**: Job title or keywords
    - **location**: Location for the search
    - **num_jobs**: Number of jobs to fetch (default: 20)
    - **remote_only**: Filter for remote jobs only
    """
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    result = await search_jobs(
        query=body.query,
        location=body.location,
        num_jobs=body.num_jobs,
        remote_only=body.remote_only
    )
    
    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result


@app.post("/api/summarize")
@limiter.limit("4/minute")
async def summarize_job_endpoint(request: Request, body: SummarizeRequest):
    """
    Summarize a job description using Groq AI.
    Rate limited to 4 requests per minute per IP.
    
    - **description**: Full job description text
    """
    if not body.description.strip():
        raise HTTPException(status_code=400, detail="Description cannot be empty")
    
    result = await summarize_job(body.description)
    
    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "job-scraper"}


# Vercel serverless handler
handler = app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
