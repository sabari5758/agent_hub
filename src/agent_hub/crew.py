import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, after_kickoff, agent, before_kickoff, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from agent_hub.schema import JobResult, TrendResult

from crewai_tools import  SerperDevTool, WebsiteSearchTool
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class AgentHub():
    """AgentHub crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    primary_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"), # Primary Key
    fallbacks=[
        # If Groq fails, LiteLLM looks for GEMINI_API_KEY in your .env
        LLM(
            model="gemini/gemini-2.0-flash",
            api_key=os.getenv("GEMINI_API_KEY")
        )
    ]
)

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    
    # config tools
    # Explicitly naming tools to prevent LLM from hallucinating incorrect tool names
    search_tool = SerperDevTool(
        name="google_search",
        description="Search the internet for up-to-date news, trends, and information."
    )
    web_tool = WebsiteSearchTool(
        name="website_scraper",
        description="Scrape and read the content of a specific website URL."
    )

    @before_kickoff
    def announce_start(self, inputs):
        print(f"🚀 [APP STARTED] Initializing Crew with inputs: {inputs}")
        return inputs

    @after_kickoff
    def announce_end(self, result):
        print(f"✅ [APP FINISHED] Data processing complete. Result length: {len(str(result))}")
        return result
    
    @agent
    def tech_scout(self) -> Agent:
        return Agent(
            config=self.agents_config['tech_scout'], # type: ignore[index]
            llm=self.primary_llm,
            tools=[self.search_tool, self.web_tool], # type: ignore[attr-defined]
            verbose=True,
            # 1. Force deterministic behavior
            temperature=0.0, 
            # 2. Disable delegation to prevent agents from trying to "invent" tools
            allow_delegation=False,
            # 3. Increase max iterations so it can recover from a small error
            max_iter=3
        )

    @agent
    def career_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['career_analyst'], # type: ignore[index]
            llm=self.primary_llm,
            tools=[self.search_tool,self.web_tool], # type: ignore[attr-defined]
            verbose=True,
            # 1. Force deterministic behavior
            temperature=0.0, 
            # 2. Disable delegation to prevent agents from trying to "invent" tools
            allow_delegation=False,
            # 3. Increase max iterations so it can recover from a small error
            max_iter=3
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
            create_directory=True,
            output_pydantic=TrendResult
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'], # type: ignore[index]
            create_directory=True,
            output_pydantic=JobResult
        )

    @crew
    def crew(self) -> Crew:
        """Creates the AgentHub crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
