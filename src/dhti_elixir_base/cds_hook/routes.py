from fastapi import FastAPI
from fastapi.testclient import TestClient
from ..mydi import get_di


def add_services(app: FastAPI, path: str = "/langserve/dhti_elixir_template"):
    @app.get(f"{path}/cds-services")
    async def cds_service():
        return get_di("cds_hook_discovery") or {"services": []}


def add_invokes(app: FastAPI, path: str = "/langserve/dhti_elixir_template"):
    @app.post(f"{path}/cds-services/dhti-service")
    async def invoke_chain(
        payload: dict,
    ):
        client = TestClient(app)
        response = client.post(f"{path}/invoke", json=payload)
        return response.json()["output"]
