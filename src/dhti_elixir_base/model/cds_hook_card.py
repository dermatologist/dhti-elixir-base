"""Pydantic Model for CDS Hook Card

Example:

{
  "summary": "Patient is at high risk for opioid overdose.",
  "detail": "According to CDC guidelines, the patient's opioid dosage should be tapered to less than 50 MME. [Link to CDC Guideline](https://www.cdc.gov/drugoverdose/prescribing/guidelines.html)",
  "indicator": "warning",
  "source": {
    "label": "CDC Opioid Prescribing Guidelines",
    "url": "https://www.cdc.gov/drugoverdose/prescribing/guidelines.html",
    "icon": "https://example.org/img/cdc-icon.png"
  },
  "links": [
    {
      "label": "View MME Conversion Table",
      "url": "https://www.cdc.gov/drugoverdose/prescribing/mme.html"
    }
  ]
}

"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class CDSHookCardSource(BaseModel):
    """Source of the CDS Hook Card"""
    label: str = Field(..., description="Label for the source of the card")
    url: Optional[str] = Field(None, description="URL for the source of the card")
    icon: Optional[str] = Field(None, description="Icon URL for the source of the card")

class CDSHookCardLink(BaseModel):
    """Link associated with the CDS Hook Card"""
    label: str = Field(..., description="Label for the link")
    url: str = Field(..., description="URL for the link")

class CDSHookCard(BaseModel):
    """CDS Hook Card Model"""
    summary: str = Field(..., description="A brief summary of the card")
    detail: Optional[str] = Field(None, description="Detailed information about the card")
    indicator: Optional[Literal["info", "warning", "hard-stop"]] = Field(
        None,
        description="Indicator for the card (e.g., 'info', 'warning', 'hard-stop')"
    )
    source: Optional[CDSHookCardSource] = Field(None, description="Source information for the card")
    links: Optional[List[CDSHookCardLink]] = Field(None, description="List of links associated with the card")
