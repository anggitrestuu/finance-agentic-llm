from crewai import Agent, Task
from langchain.tools import Tool
from typing import List, Dict

class SeniorAuditorAgent:
    def __init__(self, llm=None):
        self.llm = llm
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the Senior Auditor agent with specific traits and goals"""
        return Agent(
            role='Senior Auditor',
            goal='Create comprehensive and actionable audit plans for financial data analysis',
            backstory="""You are a highly experienced Senior Auditor with expertise in financial auditing 
            and risk assessment. Your role is to analyze audit requirements, create strategic audit plans, 
            and coordinate with IT auditors for detailed investigations. You have extensive experience in 
            identifying high-risk areas and ensuring compliance with auditing standards.""",
            verbose=True,
            llm=self.llm,
            max_iter=2
        )

    def get_task(self, problem: str) -> Task:
        return Task(
            description=f"""
            You need to do the following action in one step, and should not request additional information

            You need to make actionabe plan for the IT Auditor, in the following guidelines:
            1. Understand the specific audit cycle and assertion that are being asked
            2. Read the metadata and understand how each file and column can relate to each other in planning the audit plan
            3. Make specific and concise audit plan to be carried out by Senior IT Auditor, including the SQL statement,so it can effectively use SQL query to analyze the dataset
            4. Set specific rule and criteria, given the audit cycle and assertion
            5. Show the output in 'result' variable

            Below is the information about the cycle, assertion, and metadata:
            {problem}
            """,
            expected_output="Provide a concise and clear actionable and SQL statement for an IT auditor. Ensure it includes explicit criteria for audit goal.",
            agent=self.agent,
        )