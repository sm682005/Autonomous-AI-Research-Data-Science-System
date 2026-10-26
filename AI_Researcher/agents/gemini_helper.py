"""
Gemini Helper Module.
Standardized, fault-tolerant execution wrapper for the official google-genai SDK.
Handles structured outputs, schema validation, rate limits, and bounded retries.
"""

import json
import re
import time
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel
from google.genai import types

T = TypeVar("T", bound=BaseModel)


def clean_json_string(text: str) -> str:
    """Strips markdown code fences and cleans JSON response."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text


def generate_structured(
    client: Any,
    model: str,
    prompt: str,
    schema_cls: Type[T],
    system_instruction: Optional[str] = None,
    temperature: float = 0.2,
    max_retries: int = 3,
) -> T:
    """
    Executes a structured generation call with Gemini and returns a validated Pydantic model instance.
    Includes bounded exponential retries for rate-limiting and transient errors.
    """
    config_params: dict = {
        "temperature": temperature,
        "response_mime_type": "application/json",
        "response_schema": schema_cls,
    }
    if system_instruction:
        config_params["system_instruction"] = system_instruction

    config = types.GenerateContentConfig(**config_params)

    last_error: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )

            # Check if SDK parsed the model directly
            if hasattr(response, "parsed") and response.parsed is not None:
                if isinstance(response.parsed, schema_cls):
                    return response.parsed
                if isinstance(response.parsed, dict):
                    return schema_cls.model_validate(response.parsed)

            # Fall back to validating response.text
            raw_text = response.text or ""
            clean_text = clean_json_string(raw_text)
            return schema_cls.model_validate_json(clean_text)

        except Exception as e:
            last_error = e
            err_msg = str(e).lower()
            
            # Check for invalid credentials
            if "api key" in err_msg or "unauthenticated" in err_msg or "permission_denied" in err_msg:
                raise ValueError(
                    f"Google Gemini Authentication Error: {e}.\n"
                    "Please verify your GEMINI_API_KEY in the environment or .env file."
                ) from e
            
            # Transient or rate-limit retry
            if attempt < max_retries:
                sleep_time = attempt * 2.0
                time.sleep(sleep_time)
            else:
                break

    raise RuntimeError(
        f"Gemini generation failed after {max_retries} attempts. Last error: {last_error}"
    )
