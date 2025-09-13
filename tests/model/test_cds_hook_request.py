import pytest

@pytest.fixture(scope="session")
def cds_hook_request_model():
    from src.dhti_elixir_base.model.cds_hook_request import CDSHookRequest
    return CDSHookRequest

def test_cds_hook_request_model_import(cds_hook_request_model):
    assert cds_hook_request_model is not None