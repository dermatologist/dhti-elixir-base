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


def test_get_everything_for_patient(fhir_search, monkeypatch):
    """
    Test fetching all resources related to a specific patient using the $everything operation, with a mock response.
    """

    def _mock_get_everything_for_patient(self, patient_id):
        return {
            "entry": [
                {"resource": {"resourceType": "Patient", "id": patient_id}},
                {
                    "resource": {
                        "resourceType": "Observation",
                        "subject": {"reference": f"Patient/{patient_id}"},
                    }
                },
            ]
        }

    monkeypatch.setattr(
        "src.dhti_elixir_base.fhir.fhir_search.DhtiFhirSearch.get_everything_for_patient",
        _mock_get_everything_for_patient,
    )

    patient_id = "example"
    results = fhir_search.get_everything_for_patient(patient_id)
    assert "entry" in results
    assert len(results["entry"]) > 0
    for entry in results["entry"]:
        assert "resource" in entry


def test_get_conditions_for_patient(fhir_search, monkeypatch):
    """
    Test fetching all Condition resources related to a specific patient using a mock response.
    """

    def _mock_get_conditions_for_patient(self, patient_id):
        return {
            "entry": [
                {
                    "resource": {
                        "resourceType": "Condition",
                        "subject": {"reference": f"Patient/{patient_id}"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Condition",
                        "subject": {"reference": f"Patient/{patient_id}"},
                    }
                },
            ]
        }

    monkeypatch.setattr(
        "src.dhti_elixir_base.fhir.fhir_search.DhtiFhirSearch.get_conditions_for_patient",
        _mock_get_conditions_for_patient,
    )

    conditions = fhir_search.get_conditions_for_patient("example")
    assert "entry" in conditions
    assert len(conditions["entry"]) > 0
    for entry in conditions["entry"]:
        assert "resource" in entry
        assert entry["resource"]["resourceType"] == "Condition"
        assert entry["resource"]["subject"]["reference"] == "Patient/example"


def test_get_observations_for_patient(fhir_search, monkeypatch):
    """
    Test fetching all Observation resources related to a specific patient using a mock response.
    """

    def _mock_get_observations_for_patient(self, patient_id):
        return {
            "entry": [
                {
                    "resource": {
                        "resourceType": "Observation",
                        "subject": {"reference": f"Patient/{patient_id}"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Observation",
                        "subject": {"reference": f"Patient/{patient_id}"},
                    }
                },
            ]
        }

    monkeypatch.setattr(
        "src.dhti_elixir_base.fhir.fhir_search.DhtiFhirSearch.get_observations_for_patient",
        _mock_get_observations_for_patient,
    )

    observations = fhir_search.get_observations_for_patient("example")
    assert "entry" in observations
    assert len(observations["entry"]) > 0
    for entry in observations["entry"]:
        assert "resource" in entry
        assert entry["resource"]["resourceType"] == "Observation"
        assert entry["resource"]["subject"]["reference"] == "Patient/example"


def test_get_patient_id(fhir_search):
    """
    Test extracting patient ID from various input formats.
    """
    # Test with direct patient ID string
    patient_id = fhir_search.get_patient_id("example")
    assert patient_id == "example"

    # Test with dictionary containing 'id' key
    patient_id = fhir_search.get_patient_id({"id": "example"})
    assert patient_id == "example"

    # Test with dictionary containing 'patient' key
    patient_id = fhir_search.get_patient_id({"patient": "example"})
    assert patient_id == "example"

    # Test with dictionary containing 'Patient' key
    patient_id = fhir_search.get_patient_id({"Patient": "example"})
    assert patient_id == "example"

    # Test with dictionary containing 'subject' key
    patient_id = fhir_search.get_patient_id({"subject": "example"})
    assert patient_id == "example"

    # Test with dictionary missing patient ID keys
    patient_id = fhir_search.get_patient_id({"name": "John Doe"})
    assert patient_id is None


def test_get_procedures_for_patient(fhir_search, monkeypatch):
    """
    Test fetching all Procedure resources related to a specific patient using a mock response.
    """

    def _mock_get_procedures_for_patient(self, patient_id):
        return {
            "entry": [
                {
                    "resource": {
                        "resourceType": "Procedure",
                        "subject": {"reference": f"Patient/{patient_id}"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "Procedure",
                        "subject": {"reference": f"Patient/{patient_id}"},
                    }
                },
            ]
        }

    monkeypatch.setattr(
        "src.dhti_elixir_base.fhir.fhir_search.DhtiFhirSearch.get_procedures_for_patient",
        _mock_get_procedures_for_patient,
    )

    procedures = fhir_search.get_procedures_for_patient("example")
    assert "entry" in procedures
    assert len(procedures["entry"]) > 0
    for entry in procedures["entry"]:
        assert "resource" in entry
        assert entry["resource"]["resourceType"] == "Procedure"
        assert entry["resource"]["subject"]["reference"] == "Patient/example"


def test_get_medication_requests_for_patient(fhir_search, monkeypatch):
    """
    Test fetching all MedicationRequest resources related to a specific patient using a mock response.
    """

    def _mock_get_medication_requests_for_patient(self, patient_id):
        return {
            "entry": [
                {
                    "resource": {
                        "resourceType": "MedicationRequest",
                        "subject": {"reference": f"Patient/{patient_id}"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "MedicationRequest",
                        "subject": {"reference": f"Patient/{patient_id}"},
                    }
                },
            ]
        }

    monkeypatch.setattr(
        "src.dhti_elixir_base.fhir.fhir_search.DhtiFhirSearch.get_medication_requests_for_patient",
        _mock_get_medication_requests_for_patient,
    )

    medication_requests = fhir_search.get_medication_requests_for_patient("example")
    assert "entry" in medication_requests
    assert len(medication_requests["entry"]) > 0
    for entry in medication_requests["entry"]:
        assert "resource" in entry
        assert entry["resource"]["resourceType"] == "MedicationRequest"
        assert entry["resource"]["subject"]["reference"] == "Patient/example"


def test_get_allergy_intolerances_for_patient(fhir_search, monkeypatch):
    """
    Test fetching all AllergyIntolerance resources related to a specific patient using a mock response.
    """

    def _mock_get_allergy_intolerances_for_patient(self, patient_id):
        return {
            "entry": [
                {
                    "resource": {
                        "resourceType": "AllergyIntolerance",
                        "patient": {"reference": f"Patient/{patient_id}"},
                    }
                },
                {
                    "resource": {
                        "resourceType": "AllergyIntolerance",
                        "patient": {"reference": f"Patient/{patient_id}"},
                    }
                },
            ]
        }

    monkeypatch.setattr(
        "src.dhti_elixir_base.fhir.fhir_search.DhtiFhirSearch.get_allergy_intolerances_for_patient",
        _mock_get_allergy_intolerances_for_patient,
    )

    allergy_intolerances = fhir_search.get_allergy_intolerances_for_patient("example")
    assert "entry" in allergy_intolerances
    assert len(allergy_intolerances["entry"]) > 0
    for entry in allergy_intolerances["entry"]:
        assert "resource" in entry
        assert entry["resource"]["resourceType"] == "AllergyIntolerance"
        assert entry["resource"]["patient"]["reference"] == "Patient/example"
