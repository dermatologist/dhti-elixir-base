import pytest


@pytest.fixture(scope="session")
def cds_hook_card():
    from src.dhti_elixir_base.cds_hook import CDSHookCard

    return CDSHookCard

def test_card_model(cds_hook_card):
    card_data = {
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

    card = cds_hook_card(**card_data)
    assert card.summary == card_data["summary"]
    assert card.detail == card_data["detail"]
    assert card.indicator == card_data["indicator"]
    assert card.source.label == card_data["source"]["label"]
    assert card.source.url == card_data["source"]["url"]
    assert card.source.icon == card_data["source"]["icon"]
    assert len(card.links) == 1
    assert card.links[0].label == card_data["links"][0]["label"]
    assert card.links[0].url == card_data["links"][0]["url"]
