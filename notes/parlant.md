# Parlant Agent Integration

## Overview

The `ParlantAgent` class provides a healthcare-focused agent implementation using the [Parlant](https://github.com/emcie-co/parlant) framework. Parlant is an advanced conversational AI framework that offers sophisticated features for building context-aware, guideline-driven agents with explainability and journey management.

## What is Parlant?

Parlant is a modern framework for building conversational AI agents with the following key features:

- **Guidelines**: Behavioral rules that define how agents should respond in specific contexts
- **Journeys**: Multi-step conversational workflows that guide users through complex interactions
- **Canned Responses**: Pre-defined responses for common queries ensuring consistency
- **Explainability**: Transparent reasoning and decision tracking
- **Session Management**: Sophisticated session handling for context preservation
- **Tool Integration**: Seamless integration of external tools and services

## Architecture

### ParlantAgent Class

The `ParlantAgent` class extends `BaseAgent` and integrates Parlant's SDK for healthcare applications. It follows the same pattern as the existing `BaseAgent` class while adding Parlant-specific capabilities.

```python
from dhti_elixir_base import ParlantAgent

# Create a basic agent
agent = ParlantAgent(
    name="healthcare_assistant",
    description="Healthcare assistant for patient support",
    llm=my_llm,
)

# Get a response
response = agent.get_agent_response("I need to schedule an appointment")
```

### Key Components

#### 1. Healthcare Guidelines

The agent includes pre-configured guidelines for healthcare contexts:

- **Privacy Guideline**: Handles personal health information with HIPAA compliance
- **Emergency Guideline**: Recognizes emergency situations and provides appropriate guidance
- **Disclaimer Guideline**: Ensures medical advice requests include appropriate disclaimers
- **Medication Guideline**: Provides safe medication information guidance
- **Empathy Guideline**: Responds empathetically to patient distress
- **Clarity Guideline**: Explains medical terminology in simple language
- **Appointment Guideline**: Manages appointment scheduling workflows
- **Insurance Guideline**: Handles insurance and billing inquiries

#### 2. Healthcare Journeys

Pre-built conversational journeys for common healthcare workflows:

- **Symptom Assessment Journey**: Guides patients through symptom evaluation
  - Initial Complaint
  - Symptom Details
  - Severity Assessment
  - Recommendation

- **Appointment Booking Journey**: Manages appointment scheduling
  - Visit Reason
  - Provider Selection
  - Time Selection
  - Confirmation

- **Medication Inquiry Journey**: Provides medication information
  - Medication Identification
  - Information Type
  - Provide Information
  - Safety Reminder

#### 3. Canned Responses

Pre-defined responses for common scenarios:

- Emergency situations
- Medical disclaimers
- Privacy assurances
- Office hours
- Insurance inquiries
- Prescription refills
- Test results
- Preventive care

## Usage Examples

### Basic Usage

```python
from dhti_elixir_base import ParlantAgent
from langchain_core.language_models.fake import FakeListLLM

# Create a fake LLM for testing
llm = FakeListLLM(responses=["I understand your concern.", "Let me help you."])

# Create agent
agent = ParlantAgent(
    name="patient_assistant",
    description="Patient support assistant",
    llm=llm,
)

# Get response
response = agent.get_agent_response("I have a headache")
print(response)
```

### Accessing Guidelines and Journeys

```python
# Get all guidelines
guidelines = agent.get_guidelines()
for guideline in guidelines:
    print(f"{guideline['id']}: {guideline['condition']}")

# Get all journeys
journeys = agent.get_journeys()
for journey in journeys:
    print(f"{journey['title']}: {journey['description']}")
```

### Using Canned Responses

```python
# Get specific canned response
emergency_response = agent.get_canned_response("emergency")
disclaimer = agent.get_canned_response("medical_disclaimer")
```

### Custom Configuration

```python
# Create agent with custom Parlant parameters
agent = ParlantAgent(
    name="custom_agent",
    description="Custom healthcare agent",
    llm=my_llm,
    parlant_params={
        "max_iterations": 10,
        "custom_setting": "value",
    }
)
```

## Healthcare Domain Adaptation

The `ParlantAgent` is specifically adapted for healthcare contexts with:

### Safety Features

1. **Emergency Detection**: Automatically detects emergency keywords and provides immediate guidance
2. **Medical Disclaimer**: Always includes appropriate disclaimers for medical information
3. **Privacy Protection**: Emphasizes HIPAA compliance and data security
4. **Provider Referral**: Consistently recommends consulting healthcare providers for specific medical advice

### Empathy and Communication

1. **Empathetic Responses**: Responds with understanding to patient distress
2. **Clear Communication**: Explains medical terminology in accessible language
3. **Patient-Centered**: Focuses on patient needs and concerns
4. **Supportive Guidance**: Provides helpful information while maintaining appropriate boundaries

### Workflow Support

1. **Appointment Management**: Guides users through scheduling processes
2. **Symptom Assessment**: Structured approach to understanding patient symptoms
3. **Medication Information**: Safe delivery of medication-related information
4. **Resource Navigation**: Helps patients navigate healthcare resources

## Testing

The agent includes comprehensive unit tests covering:

- Guidelines and journeys initialization
- Canned responses availability
- Emergency detection
- Medical advice handling
- Appointment scheduling
- Prescription refills
- General health queries
- Edge cases and error handling

Run tests with:

```bash
uv run python -m pytest tests/test_parlant_agent.py -v
```

## Explainability

Parlant's explainability features allow tracking:

- Which guidelines were triggered
- Journey state transitions
- Decision reasoning
- Tool invocations
- Context usage

This is crucial for healthcare applications where understanding agent reasoning is important for trust and compliance.

## Future Improvements

### 1. Enhanced Session Management

- Implement proper session persistence across conversations
- Add session history tracking
- Enable conversation resumption
- Support multi-turn context preservation

### 2. Advanced Journey Implementation

- Complete journey state machine implementation
- Add journey branching based on user responses
- Implement journey progress tracking
- Enable journey customization per patient

### 3. Guideline Sophistication

- Add more healthcare-specific guidelines
- Implement guideline priority system
- Enable dynamic guideline loading
- Support guideline versioning

### 4. Tool Integration

- Integrate with FHIR resources for real data
- Connect to appointment scheduling systems
- Link with prescription management systems
- Add EHR query capabilities

### 5. Explainability Enhancement

- Add detailed reasoning logs
- Implement decision tree visualization
- Enable audit trail generation
- Support compliance reporting

### 6. Multi-Language Support

- Add translation capabilities
- Support cultural adaptations
- Localize medical terminology
- Adapt to regional healthcare practices

### 7. Advanced NLP Features

- Sentiment analysis for patient emotion detection
- Intent classification for better routing
- Named entity recognition for medical terms
- Symptom severity assessment

### 8. Integration Improvements

- Better integration with BaseAgent features
- Support for MCP tools from parent class
- Enhanced async operation support
- Improved error handling and recovery

### 9. Healthcare Compliance

- Add HIPAA audit logging
- Implement consent management
- Support data retention policies
- Enable anonymization features

### 10. Performance Optimization

- Implement caching for common queries
- Optimize guideline matching
- Add response time monitoring
- Support load balancing

### 11. Personalization

- Patient preference learning
- Communication style adaptation
- Provider relationship awareness
- Historical interaction consideration

### 12. Quality Assurance

- Add response quality scoring
- Implement safety checks
- Enable automated testing
- Support A/B testing

## Comparison with BaseAgent

| Feature | BaseAgent | ParlantAgent |
|---------|-----------|--------------|
| Framework | LangChain | Parlant |
| Guidelines | Manual | Built-in |
| Journeys | Not supported | Multi-step workflows |
| Canned Responses | Not available | Pre-configured |
| Explainability | Limited | Comprehensive |
| Session Management | Basic | Advanced |
| Healthcare Focus | Generic | Specialized |
| Async Support | Yes | Yes |
| Tool Integration | MCP | Parlant + MCP |

## Dependencies

The Parlant agent requires:

```toml
"parlant>=3.0.0,<4.0.0"
```

This includes all Parlant SDK dependencies for agent creation, guideline management, journey handling, and session management.

## Best Practices

1. **Always include medical disclaimers** for health-related responses
2. **Prioritize emergency detection** and appropriate routing
3. **Maintain patient privacy** and HIPAA compliance
4. **Use clear, accessible language** avoiding medical jargon
5. **Provide empathetic responses** to patient concerns
6. **Direct to healthcare providers** for specific medical advice
7. **Test thoroughly** with diverse healthcare scenarios
8. **Monitor and audit** agent interactions for quality
9. **Update guidelines regularly** based on feedback
10. **Document all customizations** for maintainability

## Limitations

Current limitations to be aware of:

1. **Session initialization**: Full Parlant session management is simplified in current implementation
2. **Async operations**: Some Parlant features require async context that may need additional setup
3. **Journey state management**: Journey transitions are defined but not fully implemented
4. **Tool integration**: Parlant tool integration is separate from LangChain tools
5. **LLM dependency**: Still relies on parent class LLM for actual response generation

## Contributing

To extend the ParlantAgent:

1. Add new guidelines in `_create_healthcare_guidelines()`
2. Define new journeys in `_create_healthcare_journeys()`
3. Add canned responses in `_create_canned_responses()`
4. Implement custom processing in `_process_with_guidelines()`
5. Add comprehensive tests for new features

## Resources

- [Parlant GitHub Repository](https://github.com/emcie-co/parlant)
- [Parlant Documentation](https://github.com/emcie-co/parlant#readme)
- [DHTI Project](https://github.com/dermatologist/dhti)
- [Healthcare AI Best Practices](https://www.ncbi.nlm.nih.gov/pmc/articles/)

## License

This implementation follows the same license as the parent project (MPL-2.0) and is compatible with Parlant's Apache-2.0 license.

## Changelog

### Version 1.0.0 (Initial Release)

- Initial ParlantAgent implementation
- Healthcare-specific guidelines (8 guidelines)
- Healthcare journeys (3 journeys)
- Canned responses (8 responses)
- Comprehensive unit tests (40+ tests)
- Documentation and usage examples
