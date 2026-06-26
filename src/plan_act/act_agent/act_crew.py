from crewai import Crew,Task,Agent,Process,LLM
from crewai.project import CrewBase,crew,agent,task
from crewai.agents.agent_builder.base_agent import BaseAgent
from . import locl_llm



@CrewBase
class PlanActCrew:
    """Act crew"""

    agents: list[BaseAgent]
    tasks: list[Task]
    agents_config="config/agents.yaml"
    tasks_config="config/tasks.yaml"
    @agent
    def executor(self)->Agent:
        return Agent(
            config=self.agents_config["executor"],# type: ignore[index]
            llm=locl_llm,
            verbose=True,
        )
    @task
    def execution_task(self)->Task:
        return Task(
            config=self.tasks_config["execution_task"]# type: ignore[index]
        )
    @crew
    def crew(self)->Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )