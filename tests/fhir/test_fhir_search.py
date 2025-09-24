import pytest


@pytest.fixture(scope="session")
def fhir_search():
    """
    Fixture for DhtiFhirSearch instance.
    Returns:
        DhtiFhirSearch: Instance of the FHIR search class.
    """
    from src.dhti_elixir_base.fhir.fhir_search import DhtiFhirSearch

    return DhtiFhirSearch()


@pytest.fixture
def mock_search(monkeypatch):
    """
    Fixture to mock DhtiFhirSearch.search method for Patient resource.
    Returns:
        function: The monkeypatched search method.
    """

    def _mock_search(self, resource_type, search_parameters=None, fhirpath=None):
        if fhirpath:
            # Return mock genders for FHIRPath test
            return ["male", "male"]
        # Return mock bundle for Patient search
        return {
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "name": [{"family": "Smith"}],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Patient",
                        "name": [{"family": "Smith"}],
                    }
                },
            ]
        }

    monkeypatch.setattr(
        "src.dhti_elixir_base.fhir.fhir_search.DhtiFhirSearch.search", _mock_search
    )


def test_fhir_search(fhir_search, mock_search):
    """
    Test searching for Patient resources with a specific family name using a mock response.
    """
    search_params = {"family": "Smith", "_count": 2}
    results = fhir_search.search(
        resource_type="Patient", search_parameters=search_params
    )
    assert "entry" in results
    assert len(results["entry"]) <= 2
    for entry in results["entry"]:
        assert "resource" in entry
        assert entry["resource"]["resourceType"] == "Patient"
        assert "name" in entry["resource"]
        family_names = [name.get("family", "") for name in entry["resource"]["name"]]
        assert any("Smith" in family for family in family_names)


def test_fhir_search_with_fhirpath(fhir_search, mock_search):
    """
    Test searching for Patient resources and applying a FHIRPath expression using a mock response.
    """
    search_params = {"family": "Smith", "_count": 2}
    fhirpath_expr = "Bundle.entry.resource.gender"
    results = fhir_search.search(
        resource_type="Patient", search_parameters=search_params, fhirpath=fhirpath_expr
    )
    assert isinstance(results, list)
    assert len(results) > 0
    for gender in results:
        assert "male" in gender


def test_get_everything_for_patient(fhir_search):
    """
    Test fetching all resources related to a specific patient using the $everything operation.
    """
    # Using a known patient ID from the public HAPI FHIR test server
    patient_id = "example"
    results = fhir_search.get_everything_for_patient(patient_id)
    print(results)
    assert "entry" in results
    assert len(results["entry"]) > 0
    for entry in results["entry"]:
        assert "resource" in entry
