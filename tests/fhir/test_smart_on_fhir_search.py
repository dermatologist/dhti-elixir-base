from unittest.mock import MagicMock, patch

import pytest

from src.dhti_elixir_base.fhir.smart_on_fhir import SmartOnFhirSearch


@pytest.fixture
def sos():
    return SmartOnFhirSearch()


def test_get_patient_id_variants(sos):
    assert sos.get_patient_id("abc") == "abc"
    assert sos.get_patient_id({"id": "abc"}) == "abc"
    assert sos.get_patient_id({"patient": "abc"}) == "abc"
    assert sos.get_patient_id({"Patient": "abc"}) == "abc"
    assert sos.get_patient_id({"subject": "abc"}) == "abc"
    assert sos.get_patient_id({"name": "John"}) is None


@patch("src.dhti_elixir_base.fhir.smart_on_fhir.requests.get")
def test_search_fallback_http(mock_get, sos):
    # Simulate unknown resource type to trigger HTTP fallback
    mock_get.return_value = MagicMock(status_code=200)
    mock_get.return_value.json.return_value = {"resourceType": "Bundle", "total": 0}
    out = sos.search("UnknownResource", {"foo": "bar"})
    assert out["resourceType"] == "Bundle"
    mock_get.assert_called_once()


@patch("src.dhti_elixir_base.fhir.smart_on_fhir.requests.get")
def test_everything_uses_bearer_when_token(mock_get, sos, monkeypatch):
    # Force a token
    sos.access_token = "token123"
    monkeypatch.setattr(sos, "_ensure_token", lambda: None)
    mock_get.return_value = MagicMock(status_code=200)
    mock_get.return_value.json.return_value = {"resourceType": "Bundle", "total": 0}
    out = sos.get_everything_for_patient("abc")
    assert out["resourceType"] == "Bundle"
    # Verify Authorization header present in call
    _, kwargs = mock_get.call_args
    headers = kwargs.get("headers", {})
    assert headers.get("Authorization") == "Bearer token123"


def test_fhirpath_filtering_in_search(sos, monkeypatch):
    # Monkeypatch to always fallback HTTP and return a predictable bundle
    def fake_get(url, params=None, headers=None, **kwargs):
        class R:
            def raise_for_status(self):
                return None

            def json(self):
                return {
                    "resourceType": "Bundle",
                    "entry": [
                        {"resource": {"resourceType": "Patient", "id": "p1"}},
                        {"resource": {"resourceType": "Patient", "id": "p2"}},
                    ],
                }

        return R()

    monkeypatch.setattr(
        "src.dhti_elixir_base.fhir.smart_on_fhir.requests.get", fake_get
    )
    out = sos.search("Patient", {}, fhirpath="entry.resource.id")
    # fhirpathpy returns list of values for the path
    assert out == ["p1", "p2"]
