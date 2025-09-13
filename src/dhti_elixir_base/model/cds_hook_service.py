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
from pydantic import BaseModel, Field

class CDSHookService(BaseModel):
    """CDS Hook Service Model"""
    hook: str = Field(..., description="The hook this service is associated with (e.g., 'patient-view')")
    name: str = Field(..., description="Name of the CDS service")
    description: Optional[str] = Field(None, description="Description of the CDS service")
    id: str = Field(..., description="Unique identifier for the CDS service")
    prefetch: Optional[dict] = Field(None, description="Prefetch templates for the CDS service")

class CDSHookServicesResponse(BaseModel):
    """Response model containing a list of CDS Hook Services"""
    services: List[CDSHookService] = Field(..., description="List of CDS Hook services available")