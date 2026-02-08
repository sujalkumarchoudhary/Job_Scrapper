"""SERP API client for fetching job listings."""
import httpx
from typing import Optional
from config import SERP_API_KEY, SERP_API_BASE_URL, DEFAULT_NUM_JOBS


async def search_jobs(
    query: str,
    location: str,
    num_jobs: int = DEFAULT_NUM_JOBS,
    remote_only: bool = False
) -> dict:
    """
    Search for jobs using SerpApi Google Jobs API.
    
    Args:
        query: Job title or keywords to search for
        location: Location for the job search
        num_jobs: Number of jobs to fetch (default: 20)
        remote_only: If True, fetch only remote jobs
    
    Returns:
        Dictionary containing job listings and metadata
    """
    if not SERP_API_KEY:
        return {
            "error": "SERP_API_KEY not configured",
            "jobs": [],
            "total": 0
        }
    
    params = {
        "engine": "google_jobs",
        "q": f"{query} {location}",
        "api_key": SERP_API_KEY,
        "hl": "en",
        "num": num_jobs
    }
    
    if remote_only:
        params["ltype"] = "1"  # Remote jobs filter
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(SERP_API_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
        
        jobs = _parse_jobs(data.get("jobs_results", []))
        
        return {
            "jobs": jobs,
            "total": len(jobs),
            "search_query": query,
            "location": location
        }
    
    except httpx.HTTPStatusError as e:
        return {
            "error": f"API request failed: {e.response.status_code}",
            "jobs": [],
            "total": 0
        }
    except Exception as e:
        return {
            "error": str(e),
            "jobs": [],
            "total": 0
        }


def _parse_jobs(jobs_data: list) -> list:
    """Parse and structure job data from SERP API response."""
    parsed_jobs = []
    
    for job in jobs_data:
        parsed_job = {
            "id": job.get("job_id", ""),
            "title": job.get("title", ""),
            "company": job.get("company_name", ""),
            "location": job.get("location", ""),
            "description": job.get("description", ""),
            "posted": job.get("detected_extensions", {}).get("posted_at", ""),
            "schedule": job.get("detected_extensions", {}).get("schedule_type", ""),
            "salary": job.get("detected_extensions", {}).get("salary", ""),
            "work_from_home": job.get("detected_extensions", {}).get("work_from_home", False),
            "thumbnail": job.get("thumbnail", ""),
            "apply_links": [
                {"platform": link.get("platform", ""), "url": link.get("link", "")}
                for link in job.get("apply_options", [])[:3]
            ],
            "highlights": {
                "qualifications": job.get("job_highlights", [{}])[0].get("items", []) if job.get("job_highlights") else [],
                "responsibilities": job.get("job_highlights", [{}])[1].get("items", []) if len(job.get("job_highlights", [])) > 1 else [],
                "benefits": job.get("job_highlights", [{}])[2].get("items", []) if len(job.get("job_highlights", [])) > 2 else []
            }
        }
        parsed_jobs.append(parsed_job)
    
    return parsed_jobs
