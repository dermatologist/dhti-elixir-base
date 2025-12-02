"""CDS Hook Request Model

Pydantic Model for CDS Hook Request.
Typically context has "patientId" and "input" keys.

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

from typing import Any

from pydantic import BaseModel, HttpUrl


class CDSHookRequest(BaseModel):
    """CDS Hook Request Model"""
    hookInstance: str | None = None
    fhirServer: HttpUrl | None = None
    fhirAuthorization: Any | None = None
    hook: str | None = None  # e.g., "patient-view", "order-select", etc.
    context: Any | None = None
    prefetch: Any | None = None
