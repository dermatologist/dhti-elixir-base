import requests
from fhirpathpy import evaluate

from ..mydi import get_di


class DhtiFhirSearch:

    def __init__(self):
        self.fhir_base_url = get_di("fhir_base_url") or "http://hapi.fhir.org/baseR4"
        self.page_size = get_di("fhir_page_size") or 10
        self.requests_kwargs = get_di("fhir_requests_kwargs") or {}
        self.access_token = get_di("fhir_access_token") or ""

    def get_patient_id(self, input_data):
        # patient_id is the value for key patientId or patient_id or id or PatientId, patientID, PatientID etc
        try:
            patient_id = (
                input_data.get("patientId")
                or input_data.get("patient_id")
                or input_data.get("id")
                or input_data.get("PatientId")
                or input_data.get("patientID")
                or input_data.get("PatientID")
                or input_data.get("ID")
                or input_data.get("Id")
                or input_data.get("patient")
                or input_data.get("Patient")
                or input_data.get("subject")
            )
            return patient_id
        except AttributeError:
            return input_data

    def _search_patient_resources(self, resource_type: str, input_data=None, fhirpath=None):
        """Internal helper to search for patient-related resources.

        This method consolidates the common search logic for patient resources,
        reducing code duplication and improving maintainability.

        Args:
            resource_type (str): FHIR resource type (e.g., "Condition", "Observation").
            input_data (dict or str): Input containing patient ID or the patient ID itself.
            fhirpath (str, optional): FHIRPath expression to apply to the results.

        Returns:
            dict: Search results from the FHIR server.
        """
        if input_data is None:
            input_data = {}
        patient_id = self.get_patient_id(input_data)
        if not patient_id:
            raise ValueError("Patient ID is required.")
        headers = {"Content-Type": "application/fhir+json"}
        search_url = f"{self.fhir_base_url}/{resource_type}"
        search_parameters = {"patient": patient_id, "_count": self.page_size}
        r = requests.get(
            search_url,
            params=search_parameters,
            headers=headers,
            **self.requests_kwargs,
        )
        r.raise_for_status()
        data = r.json()
        return evaluate(data, fhirpath, {}) if fhirpath else data

    def get_everything_for_patient(self, input_data=None, fhirpath=None):
        """Fetch all resources related to a specific patient using the $everything operation.
        Args:
            input_data (dict or str): Input containing patient ID or the patient ID itself.
            fhirpath (str, optional): FHIRPath expression to apply to the results.
        Returns:
            dict: Combined resources related to the patient.
        """
        if input_data is None:
            input_data = {}
        patient_id = self.get_patient_id(input_data)
        if not patient_id:
            raise ValueError("Patient ID is required.")
        headers = {
            "Authorization": f"Basic {self.access_token}",
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json",
        }
        everything_url = f"{self.fhir_base_url}/Patient/{patient_id}/$everything"
        r = requests.get(everything_url, headers=headers, **self.requests_kwargs)
        r.raise_for_status()
        data = r.json()
        return evaluate(data, fhirpath, {}) if fhirpath else data

    def get_conditions_for_patient(self, input_data=None, fhirpath=None):
        """Fetch all Condition resources related to a specific patient.
        Args:
            input_data (dict or str): Input containing patient ID or the patient ID itself.
            fhirpath (str, optional): FHIRPath expression to apply to the results.
        Returns:
            dict: Combined Condition resources related to the patient.
        """
        return self._search_patient_resources("Condition", input_data, fhirpath)

    def get_observations_for_patient(self, input_data=None, fhirpath=None):
        """Fetch all Observation resources related to a specific patient.
        Args:
            input_data (dict or str): Input containing patient ID or the patient ID itself.
            fhirpath (str, optional): FHIRPath expression to apply to the results.
        Returns:
            dict: Combined Observation resources related to the patient.
        """
        return self._search_patient_resources("Observation", input_data, fhirpath)

    def get_procedures_for_patient(self, input_data=None, fhirpath=None):
        """Fetch all Procedure resources related to a specific patient.
        Args:
            input_data (dict or str): Input containing patient ID or the patient ID itself.
            fhirpath (str, optional): FHIRPath expression to apply to the results.
        Returns:
            dict: Combined Procedure resources related to the patient.
        """
        return self._search_patient_resources("Procedure", input_data, fhirpath)

    def get_medication_requests_for_patient(self, input_data=None, fhirpath=None):
        """Fetch all MedicationRequest resources related to a specific patient.
        Args:
            input_data (dict or str): Input containing patient ID or the patient ID itself.
            fhirpath (str, optional): FHIRPath expression to apply to the results.
        Returns:
            dict: Combined MedicationRequest resources related to the patient.
        """
        return self._search_patient_resources("MedicationRequest", input_data, fhirpath)

    def get_allergy_intolerances_for_patient(self, input_data=None, fhirpath=None):
        """Fetch all AllergyIntolerance resources related to a specific patient.
        Args:
            input_data (dict or str): Input containing patient ID or the patient ID itself.
            fhirpath (str, optional): FHIRPath expression to apply to the results.
        Returns:
            dict: Combined AllergyIntolerance resources related to the patient.
        """
        return self._search_patient_resources("AllergyIntolerance", input_data, fhirpath)

    def search(self, resource_type="Patient", search_parameters=None, fhirpath=None):
        """Search the FHIR server and return the combined results.

        Args:
            resource_type (str): FHIR resource type to search (e.g., "Patient").
            search_parameters (dict): Query parameters per FHIR spec; _count is
                auto-set to the configured page size if absent.

        Returns:
            dict: Combined search results from the FHIR server.
        """
        if search_parameters is None:
            search_parameters = {}

        headers = {"Content-Type": "application/fhir+json"}

        if "_count" not in search_parameters:
            search_parameters["_count"] = self.page_size

        search_url = f"{self.fhir_base_url}/{resource_type}"
        r = requests.get(
            search_url,
            params=search_parameters,
            headers=headers,
            **self.requests_kwargs,
        )
        r.raise_for_status()
        data = r.json()
        return evaluate(data, fhirpath, {}) if fhirpath else data
