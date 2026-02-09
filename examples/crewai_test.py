import os
from crewai import Agent, Task, Crew, Process
from textwrap import dedent
from dhti_elixir_base import BaseChatLLM
from dhti_elixir_base.crewai import CrewAILLMWrapper

dhti_llm = BaseChatLLM(
        base_url=os.getenv("UIS_OLLAMA_URL", ""),
        model=os.getenv("UIS_OLLAMA_MODEL", ""),
        api_key=os.getenv("UIS_OLLAMA_KEY", ""),
)

dhti_llm_wrapper = CrewAILLMWrapper(dhti_llm)

print("## Welcome to the YOUR_CREW_NAME")
print("-------------------------------------------")
var_1 = (
    input(
        dedent(
            (
                f"""What is the <var_1> to pass to your crew?\n
    """
            )
        )
    ),
)
var_2 = (
    input(
        dedent(
            (
                f"""What is the <var_1> to pass to your crew?\n
    """
            )
        )
    ),
)
var_3 = (
    input(
        dedent(
            (
                f"""What is the <var_1> to pass to your crew?\n
    """
            )
        )
    ),
)
print("-------------------------------")

# Agent Definitions

agent_1 = Agent(
    role=dedent(
        (
            f"""
        Defines the agent's function within the crew. It determines the kind of tasks the agent is best suited for.
        """
        )
    ),
    backstory=dedent(
        (
            f"""
        Provides context to the agent's role and goal, enriching the interaction and collaboration dynamics.
        """
        )
    ),
    goal=dedent(
        (
            f"""
        The individual objective that the agent aims to achieve. It guides the agent's decision-making process.
        """
        )
    ),
    allow_delegation=False,
    verbose=True,
    # ↑ Whether the agent execution should be in verbose mode
    max_iter=3,
    # ↑ maximum number of iterations the agent can perform before being forced to give its best answer
    #     llm=ChatOpenAI(model_name="gpt-4", temperature=0.8)
    # ↑ uncomment to use OpenAI API + "gpt-4"
    # llm=ChatGroq(temperature=0.8, model_name="mixtral-8x7b-32768"),
    # ↑ uncomment to use Groq's API + "llama3-70b-8192"
    llm=dhti_llm_wrapper,
    # ↑ uncomment to use Groq's API + "mixtral-8x7b-32768"
)

agent_2 = Agent(
    role=dedent(
        (
            f"""
        Defines the agent's function within the crew. It determines the kind of tasks the agent is best suited for.
        """
        )
    ),
    backstory=dedent(
        (
            f"""
        Provides context to the agent's role and goal, enriching the interaction and collaboration dynamics.
        """
        )
    ),
    goal=dedent(
        (
            f"""
        The individual objective that the agent aims to achieve. It guides the agent's decision-making process.
        """
        )
    ),
    allow_delegation=False,
    verbose=True,
    # ↑ Whether the agent execution should be in verbose mode
    max_iter=3,
    # ↑ maximum number of iterations the agent can perform before being forced to give its best answer
    # llm=ChatOpenAI(model_name="gpt-4", temperature=0.8),
    # ↑ uncomment to use OpenAI API + "gpt-4"
    # llm=ChatGroq(temperature=0.8, model_name="mixtral-8x7b-32768"),
    # ↑ uncomment to use Groq's API + "llama3-70b-8192"
    llm=dhti_llm_wrapper,
    # ↑ uncomment to use Groq's API + "mixtral-8x7b-32768"
)

agent_3 = Agent(
    role=dedent(
        (
            f"""
        Defines the agent's function within the crew. It determines the kind of tasks the agent is best suited for.
        """
        )
    ),
    backstory=dedent(
        (
            f"""
        Provides context to the agent's role and goal, enriching the interaction and collaboration dynamics.
        """
        )
    ),
    goal=dedent(
        (
            f"""
        The individual objective that the agent aims to achieve. It guides the agent's decision-making process.
        """
        )
    ),
    allow_delegation=False,
    verbose=True,
    # ↑ Whether the agent execution should be in verbose mode
    max_iter=3,
    # ↑ maximum number of iterations the agent can perform before being forced to give its best answer
    # llm=ChatOpenAI(model_name="gpt-4", temperature=0.8),
    # ↑ uncomment to use OpenAI API + "gpt-4"
    # llm=ChatGroq(temperature=0.8, model_name="mixtral-8x7b-32768"),
    # ↑ uncomment to use Groq's API + "llama3-70b-8192"
    llm=dhti_llm_wrapper,
    # ↑ uncomment to use Groq's API + "mixtral-8x7b-32768"
)

# Task Definitions

task_1 = Task(
    description=dedent(
        (
            f"""
        A clear, concise statement of what the task entails.
        ---
        VARIABLE 1: "{var_1}"
        VARIABLE 2: "{var_2}"
        VARIABLE 3: "{var_3}"
        Add more variables if needed...
        """
        )
    ),
    expected_output=dedent(
        (
            f"""
        A detailed description of what the task's completion looks like.
        """
        )
    ),
    agent=agent_1,
)

task_2 = Task(
    description=dedent(
        (
            f"""
        A clear, concise statement of what the task entails.
        ---
        VARIABLE 1: "{var_1}"
        VARIABLE 2: "{var_2}"
        VARIABLE 3: "{var_3}"
        Add more variables if needed...
        """
        )
    ),
    expected_output=dedent(
        (
            f"""
        A detailed description of what the task's completion looks like.
        """
        )
    ),
    agent=agent_2,
    context=[task_1],
    # ↑ specify which task's output should be used as context for subsequent tasks
)

task_3 = Task(
    description=dedent(
        (
            f"""
        A clear, concise statement of what the task entails.
        ---
        VARIABLE 1: "{var_1}"
        VARIABLE 2: "{var_2}"
        VARIABLE 3: "{var_3}"
        Add more variables if needed...
        """
        )
    ),
    expected_output=dedent(
        (
            f"""
        A detailed description of what the task's completion looks like.
        """
        )
    ),
    agent=agent_3,
    context=[task_2],
    # ↑ specify which task's output should be used as context for subsequent tasks
)


# Get your crew to work!


def main():
    # Instantiate your crew with a sequential process
    crew = Crew(
        agents=[agent_1, agent_2, agent_3],
        tasks=[task_1, task_2, task_3],
        verbose=True,  # You can set it to True or False
        # ↑ indicates the verbosity level for logging during execution.
        process=Process.sequential,
        # ↑ the process flow that the crew will follow (e.g., sequential, hierarchical).
    )

    result = crew.kickoff()
    print(dedent(f"""\n\n########################"""))
    print(dedent(f"""## Here is your custom crew run result:"""))
    print(dedent(f"""########################\n"""))
    print(result)


if __name__ == "__main__":
    main()
