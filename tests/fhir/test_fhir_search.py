import pytest

@pytest.fixture(scope="session")
def fhir_search():
    from src.dhti_elixir_base.fhir.fhir_search import DhtiFhirSearch

    return DhtiFhirSearch()

def test_fhir_search(fhir_search):
    # Test searching for Patient resources with a specific family name
    search_params = {"family": "Smith", "_count": 2}
    results = fhir_search.search(resource_type="Patient", search_parameters=search_params)

    print(results)  # For debugging purposes
    assert "entry" in results
    assert len(results["entry"]) <= 2  # Should return at most 2 results due to _count parameter
    for entry in results["entry"]:
        assert "resource" in entry
        assert entry["resource"]["resourceType"] == "Patient"
        assert "name" in entry["resource"]
        family_names = [name.get("family", "") for name in entry["resource"]["name"]]
        assert any("Smith" in family for family in family_names)