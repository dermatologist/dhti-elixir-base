import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# parse various cds hooks request formats
def get_content_string_from_order_select(order_select):
    if order_select.get("input"):
        order_select = order_select.get("input")
    entries = order_select.get("context", {}).get("draftOrders", {}).get("entry", [])
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
    if patient_view.get("input"):
        patient_view = patient_view.get("input")
    patient_id = patient_view.get("context", {}).get("patientId")
    if patient_id:
        return patient_id
    return None

def get_context(input_data):
    try:
        order_select = get_content_string_from_order_select(input_data)
    except:
        order_select = None
    try:
        patient_id = get_patient_id_from_request(input_data)
    except:
        patient_id = None
    if input_data.get("input"):
        input_data = input_data.get("input")
    context = {}
    try:
        context = input_data.get("context", {})
    except:
        pass
    if order_select:
        context["input"] = order_select
    if patient_id:
        context["patientId"] = patient_id
    if context == {}:
        return input_data
    return context
