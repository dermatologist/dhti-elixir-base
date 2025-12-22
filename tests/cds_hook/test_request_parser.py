import pytest

from src.dhti_elixir_base.cds_hook.request_parser import get_context


@pytest.fixture(scope="session")
def inputs():
    input_1 = {"input":{
        "hookInstance": "9a9f10a0-0f99-4471-8d98-b44b854ca079",
        "hook": "order-select",
        "fhirServer": "http://hapi.fhir.org/baseR4",
        "context": {
            "patientId": "48596990",
            "userId": "Practitioner/COREPRACTITIONER1",
            "selections": ["MedicationRequest/request-123"],
            "draftOrders": {
                "resourceType": "Bundle",
                "entry": [
                    {
                        "resource": {
                            "resourceType": "MedicationRequest",
                            "id": "request-123",
                            "status": "draft",
                            "subject": {"reference": "Patient/48596990"},
                            "authoredOn": "2025-09-21",
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "CommunicationRequest",
                            "id": "commreq-20250921104547",
                            "status": "active",
                            "subject": {"reference": "Patient/48596990"},
                            "payload": [
                                {
                                    "contentString": "Hello World"
                                }
                            ],
                            "priority": "routine",
                            "authoredOn": "2025-09-21T15:45:47.640Z",
                        }
                    },
                ],
            },
        },
        "prefetch": {
            "patient": {
                "resourceType": "Patient",
                "id": "48596990",
                "meta": {
                    "versionId": "1",
                    "lastUpdated": "2025-08-06T12:52:20.638+00:00",
                    "source": "#dUTRcmjB7oZi7Gh5",
                },
                "text": {
                    "status": "generated",
                    "div": '<div xmlns="http://www.w3.org/1999/xhtml"><div class="hapiHeaderText">NuÃ±ez <b>KARLA </b></div><table class="hapiPropertyTable"><tbody><tr><td>Date of birth</td><td><span>02 January 1980</span></td></tr></tbody></table></div>',
                },
                "name": [{"family": "Karla", "given": ["NuÃ±ez"]}],
                "gender": "female",
                "birthDate": "1980-01-02",
            }
        },
    }}
    input_2 = {
   "hookInstance" : "23f1a303-991f-4118-86c5-11d99a39222e",
   "fhirServer" : "https://fhir.example.org",
   "hook" : "patient-view",
   "context" : {
     "patientId" : "1288992",
     "userId" : "Practitioner/example"
    },
   "prefetch" : {
      "patientToGreet" : {
        "resourceType" : "Patient",
        "gender" : "male",
        "birthDate" : "1925-12-23",
        "id" : "1288992",
        "active" : "true",
        }
    }
    }
    input_3 = {
        "hookInstance": "test_hook",
        "fhirServer": "http://example.com/fhir",
        "fhirAuthorization": "Bearer test_token",
        "hook": "patient-view",
        "context": {"input": "Hello"},
        "prefetch": {},
        }
    return [input_1, input_2, input_3]



def test_get_context(capsys, inputs):
    for input in inputs:
        context = get_context(input)
        assert isinstance(context, dict)
        assert "patientId" in context or "input" in context
