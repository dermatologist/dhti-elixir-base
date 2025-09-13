"""CDS Hook Request Model

Pydantic Model for CDS Hook Request

Example:
{
  "hookInstance": "d1577c69-dfbe-44ad-ba6d-3e05e953b2ea",
  "fhirServer": "https://example.com/fhir",
  "fhirAuthorization": { ... },
  "hook": "patient-view",
  "context": { ... },
  "prefetch": { ... }
}
"""

from pydantic import BaseModel, HttpUrl
from typing import Optional, Any

class CDSHookRequest(BaseModel):
    """CDS Hook Request Model"""
    hookInstance: Optional[str]
    fhirServer: Optional[HttpUrl]
    fhirAuthorization: Optional[Any]
    hook: Optional[str]  # e.g., "patient-view", "order-select", etc.
    context: Optional[Any]
    prefetch: Optional[Any]
