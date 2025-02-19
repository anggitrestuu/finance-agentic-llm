from typing import Any, Dict, Optional
from crewai import Agent, Task, LLM
from ..config import settings

class SeniorAuditorAgent:
    """
    Senior Auditor agent responsible for creating and managing audit plans.
    
    This class handles the high-level planning and strategy for financial audits,
    working with other agents to ensure comprehensive coverage and risk assessment.
    """
    
    def __init__(self):
        """
        Initialize the Senior Auditor agent
        
        Args:
            llm: Language model instance (optional)
        """
        self.llm = self._setup_llm()
        self.agent = self._create_agent()

    def _setup_llm(self) -> LLM:
        return LLM(
            model="o3-mini",
            api_key=settings.OPENAI_API_KEY,
            # temperature=0.4,
            # max_tokens=5000
        )
    
    def _create_agent(self) -> Agent:
        """
        Create and configure the Senior Auditor agent
        
        Returns:
            Agent: Configured agent instance
        """
        return Agent(
            role='Senior Auditor',
            goal='Given the input from user, make comprehensive and actionable audit plan for IT auditor',
            backstory="""You are a skilled Senior Auditor, 
                celebrated for your ability to make comprehensive and actionable audit plan for the other members given the provided information""",
            verbose=True,
            max_rpm=20,
            max_tokens=4000,
            cache=True,
            llm=self.llm,
        )
    
    def get_task(self, problem: str, category: str, schemas: Any) -> Task:
        """
        Create an audit planning task
        
        Args:
            problem: Audit problem or question to address
            category: Audit category being investigated
            schemas: Database schema information for relevant tables
            
        Returns:
            Task: Configured audit planning task
        """
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

            Database Schema Analysis:
               Schema for {category} category:
               {schemas}
               
               - Analyze table relationships and dependencies
               - Identify key data points for investigation
               - Map data flow between tables
            """,
            expected_output="Analysis of the dataset to achieve the audit goal. output of the analysis should be assigned to the 'result' variable",
            agent=self.agent,
        )