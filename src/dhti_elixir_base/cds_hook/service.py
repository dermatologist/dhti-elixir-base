"""Pydantic models for CDS Hook Service

Example:
{
  "services": [
    {
      "hook": "patient-view",
      "name": "Static CDS Service Example",
      "description": "An example of a CDS Service that returns a card with SMART app recommendations.",
      "id": "static-patient-view",
      "prefetch": {
        "patientToGreet": "Patient/{{context.patientId}}"
      }
    }
  ]
}

"""

from typing import List, Optional
from pydantic import BaseModel

class CDSHookService(BaseModel):
    """CDS Hook Service Model"""
    hook: str
    name: str
    description: Optional[str] = None
    id: str
    prefetch: Optional[dict] = None

class CDSHookServicesResponse(BaseModel):
    """Response model containing a list of CDS Hook Services"""
    services: List[CDSHookService]