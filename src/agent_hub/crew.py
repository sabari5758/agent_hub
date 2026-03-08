import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, WebsiteSearchTool
from agent_hub.schema import JobBoardResponse, TrendResponse

# Uncomment the following line to use a local model.
# from crewai_adapter import OllamaAdapter
#
# llm = OllamaAdapter(
#     model="mistral",
#     base_url="http://localhost:11434"
# )


# Use a remote LLM. You can use any of the models from
# https://github.com/a-r-j-u-n/crewai-llms
from crewai_llms import ChatGroq


@CrewBase
class AgentHub:
    """AgentHub crew."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self) -> None:
        """Initialize the AgentHub."""
        try:
            self.llm = ChatGroq(
                api_key=os.environ.get("GROQ_API_KEY"),
                model="llama3-70b-8192",
            )
        except Exception:
            from crewai_llms import ChatGoogleGenerativeAI

            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                verbose=True,
                temperature=0.5,
                google_api_key=os.environ.get("GOOGLE_API_KEY"),
            )

    @agent
    def tech_scout(self) -> Agent:
        """Return the tech scout agent."""
        return Agent(
            config=self.agents_config,
            llm=self.llm,
            tools=[SerperDevTool(), WebsiteSearchTool()],
            verbose=True,
            allow_delegation=False,
            max_iter=3,
        )

    @agent
    def career_analyst(self) -> Agent:
        """Return the career analyst agent."""
        return Agent(
            config=self.agents_config,
            llm=self.llm,
            tools=[SerperDevTool(), WebsiteSearchTool()],
            verbose=True,
            allow_delegation=False,
            max_iter=3,
        )

    @task
    def research_task(self) -> Task:
        """Return the research task."""
        return Task(
            config=self.tasks_config,
            agent=self.tech_scout(),
            output_pydantic=TrendResponse,
        )

    @task
    def analysis_task(self) -> Task:
        """Return the analysis task."""
        return Task(
            config=self.tasks_config,
            agent=self.career_analyst(),
            output_pydantic=JobBoardResponse,
        )

    @crew
    def crew(self) -> Crew:
        """Return the AgentHub crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=2,
        )

