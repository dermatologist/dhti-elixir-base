"""
Pydantic model for CDS hooks card.
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

from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Literal


class Source(BaseModel):
    label: str
    url: HttpUrl
    icon: HttpUrl


class Link(BaseModel):
    label: str
    url: HttpUrl


class CdsHookCard(BaseModel):
    summary: str
    detail: Optional[str] = None
    indicator: Literal["info", "warning", "hard-stop"]
    source: Optional[Source] = None
    links: Optional[List[Link]] = None
