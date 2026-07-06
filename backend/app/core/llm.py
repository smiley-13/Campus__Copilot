import os
import json
import threading
import logging
from pathlib import Path
from typing import Type, TypeVar, Any
from pydantic import BaseModel
from google import genai
from google.genai import types
from app.core.config import settings

logger = logging.getLogger(__name__)

# Phase 6.5: Global Request Tracker
_call_data = threading.local()

def get_gemini_calls() -> int:
    return getattr(_call_data, "calls", 0)
    
def increment_gemini_calls():
    _call_data.calls = get_gemini_calls() + 1
    
def reset_gemini_calls():
    _call_data.calls = 0

T = TypeVar('T', bound=BaseModel)

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY
    if not api_key:
        cwd = os.getcwd()
        env_path = Path(__file__).resolve().parent.parent.parent / ".env"
        logger.error(f"GEMINI_API_KEY is not set. CWD: {cwd}, Resolved .env path: {env_path}, Exists: {env_path.exists()}")
        raise ValueError(f"GEMINI_API_KEY is not set in environment variables. Checked {env_path}")
    return genai.Client(api_key=api_key)

def generate_structured_data(prompt: str, schema_class, model: str = "gemini-2.5-flash"):
    """
    Calls Gemini API and enforces a Pydantic schema response.
    """
    client = get_gemini_client()
    increment_gemini_calls()
    
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema_class,
            temperature=0.2,
        ),
    )
    
    # Parse the returned JSON string into the Pydantic model
    # Gemini returns raw JSON text that matches the schema
    result_dict = json.loads(response.text)
    return schema_class(**result_dict)

def generate_text(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """
    Standard text generation call.
    """
    client = get_gemini_client()
    increment_gemini_calls()
    
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    return response.text
