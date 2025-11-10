"""
Copyright 2025 Bell Eapen

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def remove_multiple_outer_inputs(input_data):
    # remove multiple outer inputs
    try:
        while input_data := input_data["input"]:
            pass
    except Exception:
        return input_data


# parse various cds hooks request formats
def get_content_string_from_order_select(order_select):
    order_select = remove_multiple_outer_inputs(order_select)
    entries = order_select.get("context", {}).get("draftOrders", {}).get("entry", []) # type: ignore
    # if resourceType is CommunicationRequest, return the contentString from payload
    for entry in entries:
        resource = entry.get("resource", {})
        if resource.get("resourceType") == "CommunicationRequest":
            payload = resource.get("payload", [])
            for item in payload:
                content_string = item.get("contentString")
                try:
                    return json.loads(content_string)
                except (json.JSONDecodeError, TypeError):
                    return content_string
    return None


def get_patient_id_from_request(patient_view):
    patient_view = remove_multiple_outer_inputs(patient_view)
    patient_id = patient_view.get("context", {}).get("patientId") # type: ignore
    if patient_id:
        return patient_id
    return None


def get_context(input_data):
    input_data = json.loads(input_data) if isinstance(input_data, str) else input_data

    if (
        not isinstance(input_data, dict)
        and hasattr(input_data, "model_dump_json")
        and callable(getattr(input_data, "model_dump_json", None))
    ):
        input_data = remove_multiple_outer_inputs(
            json.loads(input_data.model_dump_json())
        )
    else:
        input_data = remove_multiple_outer_inputs(input_data)

    context = {}
    try:
        context = input_data.get("context", {}) # type: ignore
    except Exception:
        pass
    try:
        order_select = get_content_string_from_order_select(input_data)
    except Exception:
        order_select = None
    try:
        patient_id = get_patient_id_from_request(input_data)
    except Exception:
        patient_id = None
    if order_select:
        context["input"] = order_select
    if patient_id:
        context["patientId"] = patient_id
    if context == {}:
        return input_data
    logger.debug(f"Extracted context: {context}")
    return context
