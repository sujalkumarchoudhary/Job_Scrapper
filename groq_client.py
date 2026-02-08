"""Groq LLM client for job summarization."""
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL


def get_client():
    """Get Groq client instance."""
    if not GROQ_API_KEY:
        return None
    return Groq(api_key=GROQ_API_KEY)


async def summarize_job(description: str) -> dict:
    """
    Summarize a job description using Groq LLM.
    
    Args:
        description: The full job description text
    
    Returns:
        Dictionary with summary and key points
    """
    client = get_client()
    
    if not client:
        return {
            "error": "GROQ_API_KEY not configured",
            "summary": "",
            "key_points": []
        }
    
    prompt = f"""Analyze this job description and provide:
1. A brief 2-3 sentence summary
2. 5 key requirements/skills needed
3. Any notable benefits mentioned

Job Description:
{description[:3000]}

Respond in this exact JSON format:
{{
    "summary": "Brief summary here",
    "key_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
    "benefits": ["benefit1", "benefit2"]
}}"""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that analyzes job descriptions. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Try to parse JSON from response
        import json
        try:
            # Handle potential markdown code blocks
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result = json.loads(result_text)
            return {
                "summary": result.get("summary", ""),
                "key_skills": result.get("key_skills", []),
                "benefits": result.get("benefits", []),
                "error": None
            }
        except json.JSONDecodeError:
            # Return raw text if JSON parsing fails
            return {
                "summary": result_text,
                "key_skills": [],
                "benefits": [],
                "error": None
            }
    
    except Exception as e:
        return {
            "error": str(e),
            "summary": "",
            "key_skills": [],
            "benefits": []
        }
