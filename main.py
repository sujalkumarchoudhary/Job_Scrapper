"""FastAPI application for Job Scraper with Rate Limiting - Vercel compatible."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
#fix

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

# Get the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")


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
    file_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    return HTMLResponse("<h1>Job Scraper</h1><p>Static files not found</p>")


@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    """Serve static files."""
    full_path = os.path.join(STATIC_DIR, file_path)
    if os.path.exists(full_path):
        # Determine content type
        if file_path.endswith(".css"):
            media_type = "text/css"
        elif file_path.endswith(".js"):
            media_type = "application/javascript"
        elif file_path.endswith(".html"):
            media_type = "text/html"
        else:
            media_type = "application/octet-stream"
        return FileResponse(full_path, media_type=media_type)
    raise HTTPException(status_code=404, detail="File not found")


@app.post("/api/search")
@limiter.limit("4/minute")
async def search_jobs_endpoint(request: Request, body: JobSearchRequest):
    """
    Search for jobs using SERP API.
    Rate limited to 4 requests per minute per IP.
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
