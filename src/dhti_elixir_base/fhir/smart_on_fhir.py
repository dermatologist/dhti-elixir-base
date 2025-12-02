import importlib

import requests
from fhirclient import client
from fhirclient.models.allergyintolerance import AllergyIntolerance
from fhirclient.models.condition import Condition
from fhirclient.models.medicationrequest import MedicationRequest
from fhirclient.models.observation import Observation
from fhirclient.models.procedure import Procedure
from fhirpathpy import evaluate

from ..mydi import get_di


class SmartOnFhirSearch:
    """SMART-on-FHIR backed search helper mirroring DhtiFhirSearch API.

    Uses fhirclient's resource model search pattern, e.g.:

            settings = { 'app_id': 'my_web_app', 'api_base': 'https://r4.smarthealthit.org' }
            smart = client.FHIRClient(settings=settings)
            patient = Patient.read('<id>', smart.server)

    Each method returns raw JSON like DhtiFhirSearch and optionally applies a
    FHIRPath expression via fhirpathpy.evaluate.
    """

    def __init__(self):
        app_id = get_di("fhir_app_id") or "my_web_app"
        base_url = get_di("fhir_base_url") or "http://hapi.fhir.org/baseR4"
        token = get_di("fhir_access_token") or ""
        settings = {
            "app_id": app_id,
            "api_base": base_url,
        }
        if token:
            settings["access_token"] = token

        self.smart = client.FHIRClient(settings=settings)
        self.fhir_base_url = base_url
        self.page_size = get_di("fhir_page_size") or 10
        self.requests_kwargs = get_di("fhir_requests_kwargs") or {}
        self.access_token = token
        # OAuth settings (optional)
        self.oauth_token_url = (
            get_di("fhir_oauth_token_url") or get_di("oauth_token_url") or None
        )
        self.oauth_client_id = (
            get_di("fhir_oauth_client_id") or get_di("oauth_client_id") or None
        )
        self.oauth_client_secret = (
            get_di("fhir_oauth_client_secret") or get_di("oauth_client_secret") or None
        )
        self.oauth_scope = get_di("fhir_oauth_scope") or get_di("oauth_scope") or None
        self.oauth_requests_kwargs = get_di("fhir_oauth_requests_kwargs") or {}
        self._token_expires_at = 0  # epoch seconds
        # Ensure any provided token is applied to the fhirclient session
        self._apply_auth_to_server()

    # ------------------------ utils ------------------------
    def _headers(self) -> dict:
        headers = {
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json",
        }
        if self.access_token and self.access_token.strip():
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _apply_auth_to_server(self) -> None:
        """Apply Authorization header to the fhirclient server session if possible."""
        try:
            server = getattr(self.smart, "server", None)
            session = getattr(server, "session", None)
            if session is not None and self.access_token:
                session.headers["Authorization"] = f"Bearer {self.access_token}"
        except Exception:
            pass

    def _fetch_token_client_credentials(self) -> None:
        """Fetch OAuth token using client_credentials flow if configured."""
        if not (
            self.oauth_token_url and self.oauth_client_id and self.oauth_client_secret
        ):
            return
        data = {"grant_type": "client_credentials"}
        if self.oauth_scope:
            data["scope"] = self.oauth_scope
        # Use HTTP Basic auth; many servers also accept in-body client credentials
        auth = (self.oauth_client_id, self.oauth_client_secret)
        r = requests.post(
            self.oauth_token_url,
            data=data,
            auth=auth,
            headers={"Accept": "application/json"},
            **self.oauth_requests_kwargs,
        )
        r.raise_for_status()
        payload = r.json() or {}
        token = payload.get("access_token")
        token_type = payload.get("token_type", "Bearer")
        expires_in = payload.get("expires_in", 0)
        if token:
            self.access_token = token if token_type.lower() == "bearer" else token
            # Set a small safety margin of 30 seconds
            import time

            self._token_expires_at = (
                int(time.time()) + int(expires_in) - 30 if expires_in else 0
            )
            self._apply_auth_to_server()

    def _ensure_token(self) -> None:
        """Ensure a valid access token is available and applied."""
        # If we already have a token and no known expiry, assume valid
        if self.access_token and self._token_expires_at == 0:
            self._apply_auth_to_server()
            return
        # If expired or missing, try to fetch
        import time

        now = int(time.time())
        if not self.access_token or (
            self._token_expires_at and now >= self._token_expires_at
        ):
            self._fetch_token_client_credentials()
            self._apply_auth_to_server()

    def _model_class(self, resource_type: str):
        """Resolve a fhirclient model class for a given resource type name.

        Returns None if the module/class cannot be resolved.
        """
        try:
            module_name = resource_type.lower()
            mod = importlib.import_module(f"fhirclient.models.{module_name}")
            return getattr(mod, resource_type)
        except Exception:
            return None

    def get_patient_id(self, input):
        # Same extraction behavior as DhtiFhirSearch
        try:
            patient_id = (
                input.get("patientId")
                or input.get("patient_id")
                or input.get("id")
                or input.get("PatientId")
                or input.get("patientID")
                or input.get("PatientID")
                or input.get("ID")
                or input.get("Id")
                or input.get("patient")
                or input.get("Patient")
                or input.get("subject")
            )
            return patient_id
        except AttributeError:
            return input

    # ---------------------- operations ---------------------
    def get_everything_for_patient(
        self, input_data: dict | str | None = None, fhirpath: str | None = None
    ):
        """Fetch resources related to a patient using $everything operation.

        Returns JSON Bundle like DhtiFhirSearch.
        """
        if input_data is None:
            input_data = {}
        patient_id = self.get_patient_id(input_data)
        if not patient_id:
            raise ValueError("Patient ID is required.")

        # Ensure token present for authenticated endpoints
        self._ensure_token()
        # Use explicit HTTP for predictable headers and testing
        path = f"Patient/{patient_id}/$everything"
        url = f"{self.fhir_base_url}/{path}"
        r = requests.get(url, headers=self._headers(), **self.requests_kwargs)
        r.raise_for_status()
        data = r.json()

        return evaluate(data, fhirpath, {}) if fhirpath else data

    def get_conditions_for_patient(
        self, input_data: dict | str | None = None, fhirpath: str | None = None
    ):
        if input_data is None:
            input_data = {}
        patient_id = self.get_patient_id(input_data)
        if not patient_id:
            raise ValueError("Patient ID is required.")
        self._ensure_token()
        search = Condition.where(
            struct={"patient": patient_id, "_count": self.page_size}
        )
        bundle = search.perform(self.smart.server)
        data = bundle.as_json() if hasattr(bundle, "as_json") else bundle
        return evaluate(data, fhirpath, {}) if fhirpath else data

    def get_observations_for_patient(
        self, input_data: dict | str | None = None, fhirpath: str | None = None
    ):
        if input_data is None:
            input_data = {}
        patient_id = self.get_patient_id(input_data)
        if not patient_id:
            raise ValueError("Patient ID is required.")
        self._ensure_token()
        search = Observation.where(
            struct={"patient": patient_id, "_count": self.page_size}
        )
        bundle = search.perform(self.smart.server)
        data = bundle.as_json() if hasattr(bundle, "as_json") else bundle
        return evaluate(data, fhirpath, {}) if fhirpath else data

    def get_procedures_for_patient(
        self, input_data: dict | str | None = None, fhirpath: str | None = None
    ):
        if input_data is None:
            input_data = {}
        patient_id = self.get_patient_id(input_data)
        if not patient_id:
            raise ValueError("Patient ID is required.")
        self._ensure_token()
        search = Procedure.where(
            struct={"patient": patient_id, "_count": self.page_size}
        )
        bundle = search.perform(self.smart.server)
        data = bundle.as_json() if hasattr(bundle, "as_json") else bundle
        return evaluate(data, fhirpath, {}) if fhirpath else data

    def get_medication_requests_for_patient(
        self, input_data: dict | str | None = None, fhirpath: str | None = None
    ):
        if input_data is None:
            input_data = {}
        patient_id = self.get_patient_id(input_data)
        if not patient_id:
            raise ValueError("Patient ID is required.")
        self._ensure_token()
        search = MedicationRequest.where(
            struct={"patient": patient_id, "_count": self.page_size}
        )
        bundle = search.perform(self.smart.server)
        data = bundle.as_json() if hasattr(bundle, "as_json") else bundle
        return evaluate(data, fhirpath, {}) if fhirpath else data

    def get_allergy_intolerances_for_patient(
        self, input_data: dict | str | None = None, fhirpath: str | None = None
    ):
        if input_data is None:
            input_data = {}
        patient_id = self.get_patient_id(input_data)
        if not patient_id:
            raise ValueError("Patient ID is required.")
        self._ensure_token()
        search = AllergyIntolerance.where(
            struct={"patient": patient_id, "_count": self.page_size}
        )
        bundle = search.perform(self.smart.server)
        data = bundle.as_json() if hasattr(bundle, "as_json") else bundle
        return evaluate(data, fhirpath, {}) if fhirpath else data

    def search(
        self,
        resource_type: str = "Patient",
        search_parameters: dict | None = None,
        fhirpath: str | None = None,
    ):
        """Generic search for any resource type.

        Tries to resolve the appropriate fhirclient model class and perform a
        model-based search; if not possible, falls back to an HTTP GET.
        """
        params = dict(search_parameters or {})
        if "_count" not in params:
            params["_count"] = self.page_size

        self._ensure_token()
        cls = self._model_class(resource_type)
        data = None
        if cls is not None and hasattr(cls, "where"):
            try:
                bundle = cls.where(struct=params).perform(self.smart.server)
                data = bundle.as_json() if hasattr(bundle, "as_json") else bundle
            except Exception:
                data = None

        if data is None:
            # Fallback to HTTP (works for unknown/extension resource types)
            url = f"{self.fhir_base_url}/{resource_type}"
            r = requests.get(
                url, params=params, headers=self._headers(), **self.requests_kwargs
            )
            r.raise_for_status()
            data = r.json()

        return evaluate(data, fhirpath, {}) if fhirpath else data
