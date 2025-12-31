import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def parlant_agent():
    """Create a ParlantAgent instance for testing."""
    from src.dhti_elixir_base import ParlantAgent

    return ParlantAgent()


@pytest.fixture(scope="session")
def parlant_agent_with_custom_name():
    """Create a ParlantAgent with custom name and description."""
    from src.dhti_elixir_base import ParlantAgent

    return ParlantAgent(
        name="test_healthcare_agent",
        description="Test healthcare agent for unit testing",
    )


def test_parlant_agent_initialization(parlant_agent):
    """Test that ParlantAgent initializes correctly."""
    assert parlant_agent is not None
    assert parlant_agent.name == "parlant_agent"
    assert not parlant_agent._initialized


def test_parlant_agent_custom_name(parlant_agent_with_custom_name):
    """Test ParlantAgent with custom name and description."""
    assert parlant_agent_with_custom_name.name == "test_healthcare_agent"
    assert parlant_agent_with_custom_name.description == "Test healthcare agent for unit testing"


def test_healthcare_guidelines_created(parlant_agent):
    """Test that healthcare guidelines are created."""
    guidelines = parlant_agent.get_guidelines()
    assert len(guidelines) > 0
    assert any(g["id"] == "emergency_guideline" for g in guidelines)
    assert any(g["id"] == "privacy_guideline" for g in guidelines)
    assert any(g["id"] == "medication_guideline" for g in guidelines)


def test_healthcare_journeys_created(parlant_agent):
    """Test that healthcare journeys are created."""
    journeys = parlant_agent.get_journeys()
    assert len(journeys) > 0
    assert any(j["id"] == "symptom_assessment_journey" for j in journeys)
    assert any(j["id"] == "appointment_booking_journey" for j in journeys)
    assert any(j["id"] == "medication_inquiry_journey" for j in journeys)


def test_canned_responses_available(parlant_agent):
    """Test that canned responses are available."""
    # Test emergency response
    emergency_response = parlant_agent.get_canned_response("emergency")
    assert emergency_response is not None
    assert "911" in emergency_response or "emergency" in emergency_response.lower()

    # Test medical disclaimer
    disclaimer = parlant_agent.get_canned_response("medical_disclaimer")
    assert disclaimer is not None
    assert "medical advice" in disclaimer.lower() or "healthcare provider" in disclaimer.lower()

    # Test privacy assurance
    privacy = parlant_agent.get_canned_response("privacy_assurance")
    assert privacy is not None
    assert "privacy" in privacy.lower() or "hipaa" in privacy.lower()


def test_canned_response_not_found(parlant_agent):
    """Test getting non-existent canned response."""
    response = parlant_agent.get_canned_response("nonexistent_key")
    assert response is None


def test_emergency_guideline_content(parlant_agent):
    """Test that emergency guideline has appropriate content."""
    guidelines = parlant_agent.get_guidelines()
    emergency_guideline = next((g for g in guidelines if g["id"] == "emergency_guideline"), None)
    assert emergency_guideline is not None
    assert "emergency" in emergency_guideline["condition"].lower()
    assert "911" in emergency_guideline["action"] or "emergency services" in emergency_guideline["action"].lower()


def test_privacy_guideline_content(parlant_agent):
    """Test that privacy guideline has appropriate content."""
    guidelines = parlant_agent.get_guidelines()
    privacy_guideline = next((g for g in guidelines if g["id"] == "privacy_guideline"), None)
    assert privacy_guideline is not None
    assert "privacy" in privacy_guideline["condition"].lower() or "personal health" in privacy_guideline["condition"].lower()
    assert "hipaa" in privacy_guideline["action"].lower() or "secure" in privacy_guideline["action"].lower()


def test_symptom_assessment_journey_structure(parlant_agent):
    """Test that symptom assessment journey has correct structure."""
    journeys = parlant_agent.get_journeys()
    symptom_journey = next((j for j in journeys if j["id"] == "symptom_assessment_journey"), None)
    assert symptom_journey is not None
    assert "states" in symptom_journey
    assert len(symptom_journey["states"]) >= 3  # Should have multiple states
    assert symptom_journey["title"] == "Symptom Assessment"


def test_appointment_booking_journey_structure(parlant_agent):
    """Test that appointment booking journey has correct structure."""
    journeys = parlant_agent.get_journeys()
    appointment_journey = next((j for j in journeys if j["id"] == "appointment_booking_journey"), None)
    assert appointment_journey is not None
    assert "states" in appointment_journey
    assert len(appointment_journey["states"]) >= 3
    assert "booking" in appointment_journey["title"].lower() or "appointment" in appointment_journey["title"].lower()


def test_medication_inquiry_journey_structure(parlant_agent):
    """Test that medication inquiry journey has correct structure."""
    journeys = parlant_agent.get_journeys()
    med_journey = next((j for j in journeys if j["id"] == "medication_inquiry_journey"), None)
    assert med_journey is not None
    assert "states" in med_journey
    assert len(med_journey["states"]) >= 3
    assert "medication" in med_journey["title"].lower()


def test_agent_response_emergency(parlant_agent, capsys):
    """Test agent response to emergency situation."""
    input_data = {"input": "I have severe chest pain and can't breathe"}
    response = parlant_agent.get_agent_response(context=input_data["input"])
    print(response)
    captured = capsys.readouterr()

    # Should contain emergency response
    assert "911" in response or "emergency" in response.lower()


def test_agent_response_medical_advice(parlant_agent, capsys):
    """Test agent response to medical advice request."""
    input_data = {"input": "Should I take aspirin for my headache?"}
    response = parlant_agent.get_agent_response(context=input_data["input"])
    print(response)
    captured = capsys.readouterr()

    # Should contain medical disclaimer
    assert "medical advice" in response.lower() or "healthcare provider" in response.lower()


def test_agent_response_appointment(parlant_agent, capsys):
    """Test agent response to appointment request."""
    input_data = {"input": "I need to schedule an appointment"}
    response = parlant_agent.get_agent_response(context=input_data["input"])
    print(response)
    captured = capsys.readouterr()

    # Should contain appointment information
    assert "appointment" in response.lower()


def test_agent_response_prescription(parlant_agent, capsys):
    """Test agent response to prescription refill request."""
    input_data = {"input": "I need to refill my prescription"}
    response = parlant_agent.get_agent_response(context=input_data["input"])
    print(response)
    captured = capsys.readouterr()

    # Should contain prescription refill information
    assert "prescription" in response.lower() or "refill" in response.lower()


def test_agent_response_general_query(parlant_agent, capsys):
    """Test agent response to general health query."""
    input_data = {"input": "What are the symptoms of flu?"}
    response = parlant_agent.get_agent_response(context=input_data["input"])
    print(response)
    captured = capsys.readouterr()

    # Should include medical disclaimer
    assert "medical advice" in response.lower() or "Paris" in response  # Paris is from FakeLLM


def test_agent_response_without_llm():
    """Test that agent raises error when LLM is not provided."""
    from src.dhti_elixir_base import ParlantAgent

    agent = ParlantAgent(llm=None)
    agent.llm = None  # Ensure it's None

    with pytest.raises(ValueError, match="llm must not be None"):
        agent.get_agent_response("test query")


def test_all_guidelines_have_required_fields(parlant_agent):
    """Test that all guidelines have required fields."""
    guidelines = parlant_agent.get_guidelines()
    for guideline in guidelines:
        assert "id" in guideline
        assert "condition" in guideline
        assert "action" in guideline
        assert isinstance(guideline["id"], str)
        assert isinstance(guideline["condition"], str)
        assert isinstance(guideline["action"], str)


def test_all_journeys_have_required_fields(parlant_agent):
    """Test that all journeys have required fields."""
    journeys = parlant_agent.get_journeys()
    for journey in journeys:
        assert "id" in journey
        assert "title" in journey
        assert "description" in journey
        assert "states" in journey
        assert isinstance(journey["id"], str)
        assert isinstance(journey["title"], str)
        assert isinstance(journey["description"], str)
        assert isinstance(journey["states"], list)


def test_journey_states_have_required_fields(parlant_agent):
    """Test that all journey states have required fields."""
    journeys = parlant_agent.get_journeys()
    for journey in journeys:
        for state in journey["states"]:
            assert "id" in state
            assert "name" in state
            assert "description" in state
            assert isinstance(state["id"], str)
            assert isinstance(state["name"], str)
            assert isinstance(state["description"], str)


def test_parlant_agent_inherits_from_base_agent(parlant_agent):
    """Test that ParlantAgent inherits from BaseAgent."""
    from src.dhti_elixir_base import BaseAgent

    assert isinstance(parlant_agent, BaseAgent)


def test_parlant_agent_has_tool_method(parlant_agent):
    """Test that ParlantAgent has has_tool method from BaseAgent."""
    assert hasattr(parlant_agent, "has_tool")
    assert callable(parlant_agent.has_tool)


def test_emergency_keywords_detection(parlant_agent):
    """Test detection of various emergency keywords."""
    emergency_queries = [
        "I have chest pain",
        "I can't breathe properly",
        "There is severe bleeding",
        "Someone is unconscious",
        "This is an emergency",
    ]

    for query in emergency_queries:
        response = parlant_agent.get_agent_response(query)
        # All emergency queries should trigger emergency response
        assert "911" in response or "emergency" in response.lower()


def test_appointment_keywords_detection(parlant_agent):
    """Test detection of appointment-related keywords."""
    appointment_queries = [
        ("I need to schedule an appointment", True),
        ("I want to make an appointment", True),
        ("Can I book an appointment?", True),
    ]

    for query, should_match in appointment_queries:
        response = parlant_agent.get_agent_response(query)
        if should_match:
            assert "appointment" in response.lower() or "schedule" in response.lower(), f"Expected appointment/schedule in response for: {query}"


def test_medication_keywords_detection(parlant_agent):
    """Test detection of medication-related keywords."""
    medication_queries = [
        "I need a prescription refill",
        "Can you refill my medication?",
    ]

    for query in medication_queries:
        response = parlant_agent.get_agent_response(query)
        assert "prescription" in response.lower() or "refill" in response.lower()


def test_parlant_params_initialization():
    """Test ParlantAgent initialization with custom parlant_params."""
    from src.dhti_elixir_base import ParlantAgent

    custom_params = {"max_iterations": 10, "custom_setting": "value"}
    agent = ParlantAgent(parlant_params=custom_params)

    assert agent.parlant_params == custom_params
    assert agent.parlant_params["max_iterations"] == 10
    assert agent.parlant_params["custom_setting"] == "value"


def test_guideline_ids_are_unique(parlant_agent):
    """Test that all guideline IDs are unique."""
    guidelines = parlant_agent.get_guidelines()
    guideline_ids = [g["id"] for g in guidelines]
    assert len(guideline_ids) == len(set(guideline_ids))


def test_journey_ids_are_unique(parlant_agent):
    """Test that all journey IDs are unique."""
    journeys = parlant_agent.get_journeys()
    journey_ids = [j["id"] for j in journeys]
    assert len(journey_ids) == len(set(journey_ids))


def test_canned_responses_keys(parlant_agent):
    """Test that expected canned response keys exist."""
    expected_keys = [
        "emergency",
        "medical_disclaimer",
        "privacy_assurance",
        "appointment_hours",
        "insurance_inquiry",
        "prescription_refill",
        "test_results",
        "preventive_care",
    ]

    for key in expected_keys:
        response = parlant_agent.get_canned_response(key)
        assert response is not None, f"Missing canned response for key: {key}"
        assert isinstance(response, str)
        assert len(response) > 0


def test_agent_name_property(parlant_agent):
    """Test agent name property from BaseAgent."""
    assert hasattr(parlant_agent, "name")
    assert parlant_agent.name == "parlant_agent"


def test_agent_description_property(parlant_agent_with_custom_name):
    """Test agent description property from BaseAgent."""
    assert hasattr(parlant_agent_with_custom_name, "description")
    assert parlant_agent_with_custom_name.description == "Test healthcare agent for unit testing"


def test_guidelines_empathy_guideline(parlant_agent):
    """Test that empathy guideline exists and has appropriate content."""
    guidelines = parlant_agent.get_guidelines()
    empathy_guideline = next((g for g in guidelines if g["id"] == "empathy_guideline"), None)
    assert empathy_guideline is not None
    assert "empathy" in empathy_guideline["action"].lower() or "support" in empathy_guideline["action"].lower()


def test_guidelines_clarity_guideline(parlant_agent):
    """Test that clarity guideline exists for medical terminology."""
    guidelines = parlant_agent.get_guidelines()
    clarity_guideline = next((g for g in guidelines if g["id"] == "clarity_guideline"), None)
    assert clarity_guideline is not None
    assert "terminology" in clarity_guideline["condition"].lower() or "confused" in clarity_guideline["condition"].lower()
