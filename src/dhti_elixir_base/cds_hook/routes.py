from fastapi import FastAPI
from fastapi.testclient import TestClient

from ..mydi import get_di


def add_services(app: FastAPI, path: str = "/langserve/dhti_elixir_template"):
    elixir_name = path.split("/")[-1]

    @app.get(f"{path}/cds-services")
    async def cds_service():
        return (
            get_di(elixir_name + "_cds_hook_discovery")
            or get_di("cds_hook_discovery")
            or {
                "services": [
                    {
                        "id": "dhti-service",
                        "hook": "order-select",
                        "title": "DHTI Order Assistant",
                        "description": "Provides suggestions and actions for selected draft orders, including handling CommunicationRequest resources.",
                        "prefetch": {
                            "patient": "Patient/{{context.patientId}}",
                            "draftOrders": "Bundle?patient={{context.patientId}}&status=draft",
                        },
                        "scopes": [
                            "launch",
                            "patient/Patient.read",
                            "user/Practitioner.read",
                            "patient/CommunicationRequest.read",
                        ],
                        "metadata": {
                            "author": "DHTI CDS Team",
                            "version": "1.0.0",
                            "supportedResources": [
                                "CommunicationRequest",
                            ],
                        },
                    }
                ]
            }
        )


def add_invokes(app: FastAPI, path: str = "/langserve/dhti_elixir_template"):
    @app.post(f"{path}/cds-services/dhti-service")
    async def invoke_chain(
        payload: dict,
    ):
        client = TestClient(app)
        response = client.post(f"{path}/invoke", json=_add_inputs(payload))
        data = response.json()
        return data["output"] if "output" in data else data


def _add_inputs(payload: dict):
    _input = {}
    _input["input"] = {}
    _input["input"]["input"] = payload
    return _input
