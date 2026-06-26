from crewai import Task,Agent,Crew,Process,LLM
from crewai.project import CrewBase,crew,agent,task
from crewai.agents.agent_builder.base_agent import BaseAgent
from . import local_llm

@CrewBase
class PlanCrew:
    """Plan crew"""
    agents: list[BaseAgent]
    tasks: list[Task]
    agents_config="config/agents.yaml"
    tasks_config="config/tasks.yaml"
    @task
    def planning_task(self)->Task:
        """ task """
        return Task(
            config= self.tasks_config["planning_task"]# type: ignore[index]
        )
    @agent
    def planner(self)->Agent:
        return Agent(
            config=self.agents_config["planner"],# type: ignore[index]
            llm=local_llm,
             verbose=True
        )
    @crew
    def crew(self)-> Crew:
        """Creates the HelloAgent crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )