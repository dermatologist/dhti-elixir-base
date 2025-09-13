import pytest

@pytest.fixture(scope="session")
def cds_hook_service_model():
    from src.dhti_elixir_base.model.cds_hook_service import CDSHookService, CDSHookServicesResponse
    return CDSHookService, CDSHookServicesResponse

def test_cds_hook_service_model_import(cds_hook_service_model):
    CDSHookService, CDSHookServicesResponse = cds_hook_service_model
    assert CDSHookService is not None
    assert CDSHookServicesResponse is not None