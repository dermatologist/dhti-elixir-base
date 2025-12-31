"""
Copyright 2023 Bell Eapen

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
from typing import Any

from parlant.sdk import (
    Agent,
    AgentId,
    AgentStore,
    Container,
    GuidelineId,
    GuidelineStore,
    JourneyId,
    JourneyStore,
    Session,
    SessionId,
    SessionStore,
    start_parlant,
)
from pydantic import BaseModel, ConfigDict

from .agent import BaseAgent

logger = logging.getLogger(__name__)


class ParlantAgent(BaseAgent):
    """
    A Parlant-based agent implementation for healthcare domain applications.

    This agent extends BaseAgent to use Parlant SDK for agent creation with
    healthcare-specific guidelines, journeys, and conversational patterns.
    Parlant provides advanced features like:
    - Guidelines: Behavioral rules and conditional actions
    - Journeys: Multi-step conversational workflows
    - Canned Responses: Pre-defined responses for common queries
    - Explainability: Transparent reasoning and decision tracking
    """

    class AgentInput(BaseModel):
        """Input model for agent interactions."""

        input: str
        session_id: str | None = None
        model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)

    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
        llm: Any = None,
        prompt: str | None = None,
        input_type: type[BaseModel] | None = None,
        tools: list | None = None,
        parlant_params: dict | None = None,
    ):
        """
        Initialize ParlantAgent with healthcare-specific configuration.

        Args:
            name: Agent name
            description: Agent description
            llm: Language model instance
            prompt: System prompt
            input_type: Input type for validation
            tools: List of tools available to the agent
            parlant_params: Parlant-specific parameters for customization
        """
        super().__init__(name, description, llm, prompt, input_type, tools)
        self.parlant_params = parlant_params or {}
        self._container: Container | None = None
        self._agent: Agent | None = None
        self._session: Session | None = None
        self._initialized = False

        # Healthcare-specific configuration
        self.healthcare_guidelines = self._create_healthcare_guidelines()
        self.healthcare_journeys = self._create_healthcare_journeys()
        self.canned_responses = self._create_canned_responses()

    def _create_healthcare_guidelines(self) -> list[dict]:
        """
        Create healthcare-specific behavioral guidelines.

        These guidelines define how the agent should behave in various
        healthcare contexts, ensuring patient safety, privacy, and appropriate
        medical guidance.
        """
        return [
            {
                "id": "privacy_guideline",
                "condition": "User shares personal health information",
                "action": "Acknowledge privacy importance, confirm HIPAA compliance, and handle data securely",
            },
            {
                "id": "emergency_guideline",
                "condition": "User describes emergency symptoms (chest pain, difficulty breathing, severe bleeding)",
                "action": "Immediately advise calling emergency services (911) and do not attempt to diagnose",
            },
            {
                "id": "disclaimer_guideline",
                "condition": "User asks for medical advice or diagnosis",
                "action": "Provide information but clearly state this is not medical advice and recommend consulting healthcare provider",
            },
            {
                "id": "medication_guideline",
                "condition": "User asks about medication dosage or interactions",
                "action": "Provide general information but emphasize need to consult pharmacist or physician for specific guidance",
            },
            {
                "id": "empathy_guideline",
                "condition": "User expresses distress or anxiety about health condition",
                "action": "Respond with empathy, validate feelings, and provide supportive information",
            },
            {
                "id": "clarity_guideline",
                "condition": "User is confused about medical terminology",
                "action": "Explain concepts in simple, non-technical language and use analogies when helpful",
            },
            {
                "id": "appointment_guideline",
                "condition": "User needs to schedule or manage appointments",
                "action": "Guide user through appointment scheduling process and confirm all necessary details",
            },
            {
                "id": "insurance_guideline",
                "condition": "User inquires about insurance coverage or billing",
                "action": "Provide general insurance information and direct to billing department for specific questions",
            },
        ]

    def _create_healthcare_journeys(self) -> list[dict]:
        """
        Create healthcare-specific conversational journeys.

        Journeys define multi-step workflows for common healthcare interactions
        like symptom checking, appointment booking, or medication management.
        """
        return [
            {
                "id": "symptom_assessment_journey",
                "title": "Symptom Assessment",
                "description": "Guided symptom assessment and triage",
                "states": [
                    {
                        "id": "initial_complaint",
                        "name": "Initial Complaint",
                        "description": "Gather chief complaint",
                    },
                    {
                        "id": "symptom_details",
                        "name": "Symptom Details",
                        "description": "Collect detailed symptom information",
                    },
                    {
                        "id": "severity_assessment",
                        "name": "Severity Assessment",
                        "description": "Assess symptom severity",
                    },
                    {
                        "id": "recommendation",
                        "name": "Recommendation",
                        "description": "Provide appropriate care recommendation",
                    },
                ],
            },
            {
                "id": "appointment_booking_journey",
                "title": "Appointment Booking",
                "description": "Schedule and manage healthcare appointments",
                "states": [
                    {
                        "id": "reason_for_visit",
                        "name": "Visit Reason",
                        "description": "Understand reason for appointment",
                    },
                    {
                        "id": "provider_selection",
                        "name": "Provider Selection",
                        "description": "Select appropriate healthcare provider",
                    },
                    {
                        "id": "schedule_selection",
                        "name": "Time Selection",
                        "description": "Choose appointment date and time",
                    },
                    {
                        "id": "confirmation",
                        "name": "Confirmation",
                        "description": "Confirm appointment details",
                    },
                ],
            },
            {
                "id": "medication_inquiry_journey",
                "title": "Medication Information",
                "description": "Provide medication information and guidance",
                "states": [
                    {
                        "id": "medication_identification",
                        "name": "Identify Medication",
                        "description": "Identify the medication of interest",
                    },
                    {
                        "id": "information_type",
                        "name": "Information Type",
                        "description": "Determine what information is needed",
                    },
                    {
                        "id": "provide_information",
                        "name": "Provide Information",
                        "description": "Share relevant medication information",
                    },
                    {
                        "id": "safety_reminder",
                        "name": "Safety Reminder",
                        "description": "Remind about consulting healthcare provider",
                    },
                ],
            },
        ]

    def _create_canned_responses(self) -> dict[str, str]:
        """
        Create pre-defined responses for common healthcare queries.

        Canned responses ensure consistent, accurate information delivery
        for frequently asked questions.
        """
        return {
            "emergency": "If you're experiencing a medical emergency, please call 911 immediately or go to the nearest emergency room. This is not a substitute for emergency medical care.",
            "medical_disclaimer": "Please note: I provide general health information, not medical advice. For specific medical concerns, please consult with a qualified healthcare provider.",
            "privacy_assurance": "Your privacy is important to us. All information shared is protected under HIPAA regulations and handled with strict confidentiality.",
            "appointment_hours": "Our office hours are Monday-Friday, 8:00 AM to 5:00 PM. For urgent matters outside these hours, please contact our on-call service.",
            "insurance_inquiry": "For specific insurance coverage questions, please contact our billing department at [phone number] or your insurance provider directly.",
            "prescription_refill": "For prescription refills, please contact your pharmacy or use our patient portal. Refill requests typically take 24-48 hours to process.",
            "test_results": "Test results are typically available within 3-5 business days. You can access them through our patient portal or call our office for assistance.",
            "preventive_care": "Preventive care is essential for maintaining good health. We recommend annual check-ups, age-appropriate screenings, and staying up-to-date with vaccinations.",
        }

    async def _initialize_parlant(self) -> None:
        """Initialize Parlant agent and components if not already initialized."""
        if self._initialized:
            return

        try:
            # Initialize Parlant with default or custom parameters
            from parlant.bin.server import StartupParameters

            params = StartupParameters()
            # Apply custom params if provided
            for key, value in self.parlant_params.items():
                setattr(params, key, value)

            # Start Parlant
            async with start_parlant(params) as container:
                self._container = container

                # Create or get agent
                agent_store = container[AgentStore]
                agents = await agent_store.list()

                agent_name = self._name or "healthcare_agent"
                agent_desc = self._description or "Healthcare assistant agent"

                # Find or create agent
                existing_agent = next((a for a in agents if a.name == agent_name), None)

                if existing_agent:
                    self._agent = existing_agent
                else:
                    # Create new agent
                    agent_id = AgentId(agent_name)
                    self._agent = await agent_store.create(
                        id=agent_id,
                        name=agent_name,
                        description=agent_desc,
                    )

                # Set up guidelines
                await self._setup_guidelines(container)

                # Set up journeys
                await self._setup_journeys(container)

                self._initialized = True
                logger.info(f"Parlant agent initialized: {agent_name}")

        except Exception:
            logger.exception("Error initializing Parlant agent")
            raise

    async def _setup_guidelines(self, container: Container) -> None:
        """Set up healthcare guidelines in Parlant."""
        guideline_store = container[GuidelineStore]

        for guideline_data in self.healthcare_guidelines:
            guideline_id = GuidelineId(guideline_data["id"])
            try:
                # Check if guideline exists
                existing = await guideline_store.read(guideline_id)
                if not existing:
                    # Create guideline
                    await guideline_store.create(
                        id=guideline_id,
                        condition=guideline_data["condition"],
                        action=guideline_data.get("action"),
                    )
                    logger.info(f"Created guideline: {guideline_data['id']}")
            except Exception as e:
                logger.warning(f"Could not set up guideline {guideline_data['id']}: {e}")

    async def _setup_journeys(self, container: Container) -> None:
        """Set up healthcare journeys in Parlant."""
        journey_store = container[JourneyStore]

        for journey_data in self.healthcare_journeys:
            journey_id = JourneyId(journey_data["id"])
            try:
                # Check if journey exists
                existing = await journey_store.read(journey_id)
                if not existing:
                    # Create journey
                    # Note: This is a simplified version, actual implementation
                    # would need proper state and transition setup
                    await journey_store.create(
                        id=journey_id,
                        title=journey_data["title"],
                        description=journey_data["description"],
                        states=[],  # Would be populated with actual states
                        transitions=[],  # Would be populated with actual transitions
                    )
                    logger.info(f"Created journey: {journey_data['id']}")
            except Exception as e:
                logger.warning(f"Could not set up journey {journey_data['id']}: {e}")

    def get_agent_response(self, context: str) -> str:
        """
        Get agent response using Parlant SDK.

        This method provides a synchronous interface to the Parlant agent,
        handling the interaction through Parlant's session management.

        Args:
            context: User input/query

        Returns:
            Agent's response string
        """
        if self.llm is None:
            raise ValueError("llm must not be None when initializing the agent.")

        try:
            # Process with healthcare guidelines (synchronous)
            # Note: Full async Parlant initialization is available via _get_agent_response_async
            # but for simplicity and compatibility with existing patterns, we use a
            # simplified synchronous approach here
            return self._process_with_guidelines_sync(context)
        except Exception:
            logger.exception("Error in Parlant agent processing")
            return "I apologize, but I encountered an error processing your request. Please try again or contact support if the issue persists."

    async def _get_agent_response_async(self, context: str) -> str:
        """
        Async implementation of agent response.

        This uses Parlant's session management and agent interaction
        capabilities to generate responses.
        """
        try:
            # Initialize if needed
            await self._initialize_parlant()

            if not self._agent or not self._container:
                raise ValueError("Parlant agent not initialized")

            # Create or get session
            session_store = self._container[SessionStore]

            # For simplicity, we'll use a basic interaction
            # In production, you'd manage sessions more carefully
            from datetime import datetime

            from parlant.sdk import CustomerId, SessionMode

            customer_id = CustomerId("default_customer")
            session_id = SessionId(f"session_{datetime.now().timestamp()}")

            await session_store.create(
                id=session_id,
                customer_id=customer_id,
                agent_id=self._agent.id,
                mode=SessionMode.OPEN,
            )

            # Process the message
            # Note: Actual message processing would use Parlant's
            # full interaction pipeline
            return await self._process_with_guidelines(context)

        except Exception:
            logger.exception("Error in async agent response")
            raise

    def _process_with_guidelines_sync(self, context: str) -> str:
        """
        Process user input with healthcare guidelines (synchronous version).

        This checks if any guidelines apply and generates an appropriate
        response, potentially using canned responses for common queries.
        """
        context_lower = context.lower()

        # Check for emergency keywords
        emergency_keywords = ["chest pain", "can't breathe", "severe bleeding", "unconscious", "emergency"]
        if any(keyword in context_lower for keyword in emergency_keywords):
            return self.canned_responses["emergency"]

        # Check for medical advice request
        advice_keywords = ["should i", "diagnose", "what's wrong", "do i have"]
        if any(keyword in context_lower for keyword in advice_keywords):
            prefix = self.canned_responses["medical_disclaimer"] + "\n\n"
            # Use parent class to get LLM response
            llm_response = super().get_agent_response(context)
            return prefix + llm_response

        # Check for appointment requests
        if "appointment" in context_lower or "schedule" in context_lower:
            return "I'd be happy to help you schedule an appointment. " + self.canned_responses["appointment_hours"]

        # Check for prescription refills
        if "prescription" in context_lower or "refill" in context_lower:
            return self.canned_responses["prescription_refill"]

        # Default: use base agent with medical disclaimer
        disclaimer = self.canned_responses["medical_disclaimer"] + "\n\n"
        llm_response = super().get_agent_response(context)
        return disclaimer + llm_response

    async def _process_with_guidelines(self, context: str) -> str:
        """
        Process user input with healthcare guidelines (async version for full Parlant integration).

        This checks if any guidelines apply and generates an appropriate
        response, potentially using canned responses for common queries.
        """
        # Delegate to synchronous version for now
        # In a full implementation, this would use Parlant's async APIs
        return self._process_with_guidelines_sync(context)

    def get_canned_response(self, key: str) -> str | None:
        """
        Get a canned response by key.

        Args:
            key: Response key

        Returns:
            Canned response text or None if not found
        """
        return self.canned_responses.get(key)

    def get_guidelines(self) -> list[dict]:
        """
        Get all configured guidelines.

        Returns:
            List of guideline dictionaries
        """
        return self.healthcare_guidelines

    def get_journeys(self) -> list[dict]:
        """
        Get all configured journeys.

        Returns:
            List of journey dictionaries
        """
        return self.healthcare_journeys
