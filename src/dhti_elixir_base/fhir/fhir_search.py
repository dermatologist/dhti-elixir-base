import os
import requests
from ..mydi import get_di

class DhtiFhirSearch:

    def __init__(self):
        os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
        self.fhir_base_url = get_di("fhir_base_url") or "http://hapi.fhir.org/baseR4"
        self.page_size = get_di("fhir_page_size") or 10
        self.requests_kwargs = get_di("fhir_requests_kwargs") or {}



    def search(self, resource_type="Patient", search_parameters={}):
        """Search the FHIR server and return the combined results.

        Args:
            resource_type (str): FHIR resource type to search (e.g., "Patient").
            search_parameters (dict): Query parameters per FHIR spec; _count is
                auto-set to the configured page size if absent.

        Returns:
            dict: Combined search results from the FHIR server.
        """

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
        return r.json()
