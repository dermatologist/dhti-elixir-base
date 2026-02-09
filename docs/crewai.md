# CrewAI Integration

The `dhti-elixir-base` package provides wrapper classes that enable seamless integration between DHTI's LangChain-based components and the [CrewAI](https://www.crewai.com/) framework. This allows you to leverage DHTI's healthcare-focused AI tooling within CrewAI's multi-agent orchestration system.

## Installation

To use the CrewAI integration, install `dhti-elixir-base` with the optional `crewai` dependency:

```bash
pip install dhti-elixir-base[crewai]
```

This will install both the core package and the required CrewAI dependencies.

## Overview

The CrewAI module provides four main wrapper classes:

1. **CrewAILLMWrapper**: Adapts `BaseLLM` and `BaseChatLLM` for use with CrewAI
2. **CrewAIAgentWrapper**: Wraps `BaseAgent` to create CrewAI-compatible agents
3. **CrewAIChainToolWrapper**: Converts `BaseChain` into a CrewAI tool
4. **CrewAILangChainToolWrapper**: Adapts standard LangChain tools for CrewAI

## Usage Examples

### Wrapping LLMs for CrewAI

DHTI's `BaseLLM` and `BaseChatLLM` can be wrapped for use with CrewAI agents:

```python
from dhti_elixir_base import BaseChatLLM
from dhti_elixir_base.crewai import CrewAILLMWrapper

# Create a DHTI LLM instance
dhti_llm = BaseChatLLM(
    base_url="https://api.example.com/chat",
    model="gpt-4",
    api_key="your-api-key",
    temperature=0.7
)

# Wrap it for use with CrewAI
crewai_llm = CrewAILLMWrapper(llm=dhti_llm)

# Now use it with CrewAI agents
from crewai import Agent

agent = Agent(
    role="Medical Assistant",
    goal="Assist with medical queries",
    backstory="An experienced medical AI assistant",
    llm=crewai_llm
)
```

### Wrapping Agents for CrewAI

Convert DHTI's `BaseAgent` into a CrewAI-compatible agent:

```python
from dhti_elixir_base import BaseAgent, BaseChatLLM
from dhti_elixir_base.crewai import CrewAIAgentWrapper

# Create a DHTI agent
llm = BaseChatLLM(
    base_url="https://api.example.com/chat",
    model="gpt-4",
    api_key="your-api-key"
)

dhti_agent = BaseAgent(
    name="medical_analyzer",
    description="Analyzes medical records and provides insights",
    llm=llm,
    prompt="You are a medical record analyzer. Provide accurate insights."
)

# Wrap it for CrewAI
crewai_agent = CrewAIAgentWrapper(
    agent=dhti_agent,
    role="Medical Record Analyzer",
    goal="Analyze patient records and identify key insights",
    backstory="A specialized AI trained on medical data analysis"
)

# Use it in a CrewAI crew
from crewai import Crew, Task

task = Task(
    description="Analyze the patient's medical history",
    agent=crewai_agent
)

crew = Crew(
    agents=[crewai_agent],
    tasks=[task]
)
```

### Using Chains as Tools in CrewAI

Convert DHTI's `BaseChain` into a tool that can be used by CrewAI agents:

```python
from dhti_elixir_base import BaseChain
from dhti_elixir_base.crewai import CrewAIChainToolWrapper
from crewai import Agent, Task, Crew

# Create a DHTI chain
class MedicalAnalysisChain(BaseChain):
    def __init__(self):
        super().__init__(
            name="medical_analysis",
            description="Analyzes medical records and provides insights"
        )

    # Implement your chain logic here

chain = MedicalAnalysisChain()

# Wrap it as a CrewAI tool
analysis_tool = CrewAIChainToolWrapper(
    chain=chain,
    name="Medical Analysis Tool",
    description="Analyzes medical records and provides diagnostic insights"
)

# Use the tool with a CrewAI agent
agent = Agent(
    role="Medical Assistant",
    goal="Provide medical insights",
    backstory="An AI assistant specialized in medical analysis",
    tools=[analysis_tool]
)

task = Task(
    description="Analyze this patient's symptoms: fever, cough, fatigue",
    agent=agent
)

crew = Crew(
    agents=[agent],
    tasks=[task]
)

result = crew.kickoff()
print(result)
```

### Using LangChain Tools with CrewAI

Adapt standard LangChain tools for use in CrewAI:

```python
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from dhti_elixir_base.crewai import CrewAILangChainToolWrapper
from crewai import Agent, Task, Crew

# Create a LangChain tool
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

# Wrap it for CrewAI
wiki_tool = CrewAILangChainToolWrapper(langchain_tool=wikipedia)

# Use it with a CrewAI agent
researcher = Agent(
    role="Medical Researcher",
    goal="Research medical conditions and treatments",
    backstory="A researcher specializing in medical information",
    tools=[wiki_tool]
)

task = Task(
    description="Research the latest information about diabetes",
    agent=researcher
)

crew = Crew(
    agents=[researcher],
    tasks=[task]
)

result = crew.kickoff()
print(result)
```

## Complete Example: Multi-Agent Medical System

Here's a complete example combining multiple wrappers in a CrewAI crew:

```python
from dhti_elixir_base import BaseChatLLM, BaseAgent, BaseChain
from dhti_elixir_base.crewai import (
    CrewAILLMWrapper,
    CrewAIAgentWrapper,
    CrewAIChainToolWrapper
)
from crewai import Crew, Task

# Create shared LLM
llm = BaseChatLLM(
    base_url="https://api.example.com/chat",
    model="gpt-4",
    api_key="your-api-key"
)
crewai_llm = CrewAILLMWrapper(llm=llm)

# Create a diagnostic chain as a tool
class DiagnosticChain(BaseChain):
    def __init__(self):
        super().__init__(
            name="diagnostic_tool",
            description="Provides diagnostic suggestions based on symptoms"
        )

diagnostic_tool = CrewAIChainToolWrapper(
    chain=DiagnosticChain(),
    name="Diagnostic Tool",
    description="Analyzes symptoms and suggests possible diagnoses"
)

# Create multiple agents
triage_agent = Agent(
    role="Triage Nurse",
    goal="Assess patient symptoms and prioritize care",
    backstory="An experienced triage nurse with 10 years of experience",
    llm=crewai_llm,
    tools=[diagnostic_tool]
)

specialist_agent = Agent(
    role="Medical Specialist",
    goal="Provide detailed medical analysis and recommendations",
    backstory="A board-certified physician specializing in internal medicine",
    llm=crewai_llm
)

# Create tasks
triage_task = Task(
    description="Assess the patient presenting with: severe headache, fever, and stiff neck",
    agent=triage_agent,
    expected_output="Priority assessment and initial diagnosis suggestions"
)

specialist_task = Task(
    description="Review triage assessment and provide detailed medical recommendations",
    agent=specialist_agent,
    expected_output="Detailed medical analysis and treatment recommendations"
)

# Create and run the crew
medical_crew = Crew(
    agents=[triage_agent, specialist_agent],
    tasks=[triage_task, specialist_task],
    verbose=True
)

result = medical_crew.kickoff()
print("\n=== Medical Analysis Results ===")
print(result)
```

## API Reference

### CrewAILLMWrapper

```python
CrewAILLMWrapper(llm: BaseLLM | BaseChatLLM, **kwargs)
```

Wraps DHTI's `BaseLLM` or `BaseChatLLM` for use with CrewAI.

**Parameters:**
- `llm`: An instance of `BaseLLM` or `BaseChatLLM`
- `**kwargs`: Additional keyword arguments passed to the CrewAI LLM

**Methods:**
- `call(messages, *args, **kwargs)`: Invokes the underlying LLM with the provided messages

### CrewAIAgentWrapper

```python
CrewAIAgentWrapper(
    agent: BaseAgent,
    role: str | None = None,
    goal: str | None = None,
    backstory: str | None = None,
    **kwargs
)
```

Wraps DHTI's `BaseAgent` to create a CrewAI-compatible agent.

**Parameters:**
- `agent`: An instance of `BaseAgent`
- `role`: The role of the agent (defaults to agent's description)
- `goal`: The goal of the agent (defaults to agent's name)
- `backstory`: The backstory of the agent
- `**kwargs`: Additional keyword arguments passed to the CrewAI Agent

**Methods:**
- `execute_task(task, *args, **kwargs)`: Executes a task using the underlying DHTI agent

### CrewAIChainToolWrapper

```python
CrewAIChainToolWrapper(
    chain: BaseChain,
    name: str | None = None,
    description: str | None = None,
    **kwargs
)
```

Wraps DHTI's `BaseChain` as a CrewAI tool.

**Parameters:**
- `chain`: An instance of `BaseChain`
- `name`: Name of the tool (defaults to chain's name)
- `description`: Description of the tool (defaults to chain's description)
- `**kwargs`: Additional keyword arguments

**Methods:**
- `_run(*args, **kwargs)`: Executes the underlying chain

### CrewAILangChainToolWrapper

```python
CrewAILangChainToolWrapper(langchain_tool: LangChainBaseTool, **kwargs)
```

Wraps a LangChain tool for use in CrewAI.

**Parameters:**
- `langchain_tool`: An instance of LangChain `BaseTool` or compatible tool
- `**kwargs`: Additional keyword arguments

**Methods:**
- `_run(*args, **kwargs)`: Executes the underlying LangChain tool

## Best Practices

1. **LLM Configuration**: Configure DHTI LLMs with appropriate temperature and token limits before wrapping them for CrewAI use.

2. **Agent Design**: When creating agents, provide clear roles, goals, and backstories to help CrewAI coordinate agent interactions effectively.

3. **Tool Documentation**: Provide detailed descriptions for chain tools so that CrewAI agents can understand when and how to use them.

4. **Error Handling**: Implement proper error handling in your DHTI chains and agents to ensure graceful failures in the CrewAI framework.

5. **Testing**: Test your wrapped components individually before integrating them into a full CrewAI crew.

## Limitations and Considerations

- The wrappers adapt interfaces between DHTI and CrewAI, but may not support all features of either framework
- Some advanced CrewAI features may require additional customization
- Performance characteristics may differ from native CrewAI or DHTI implementations
- Always test thoroughly in your specific use case

## Related Documentation

- [DHTI Overview](https://github.com/dermatologist/dhti)
- [CrewAI Documentation](https://docs.crewai.com/)
- [LangChain Documentation](https://python.langchain.com/)

## Support

For issues or questions:
- GitHub Issues: [dhti-elixir-base issues](https://github.com/dermatologist/dhti-elixir-base/issues)
- DHTI Home: [https://github.com/dermatologist/dhti](https://github.com/dermatologist/dhti)
