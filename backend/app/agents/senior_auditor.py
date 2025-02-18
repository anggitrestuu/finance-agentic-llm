from typing import Any, Dict, Optional
from crewai import Agent, Task

class SeniorAuditorAgent:
    """
    Senior Auditor agent responsible for creating and managing audit plans.
    
    This class handles the high-level planning and strategy for financial audits,
    working with other agents to ensure comprehensive coverage and risk assessment.
    """
    
    def __init__(self, llm: Optional[Any] = None):
        """
        Initialize the Senior Auditor agent
        
        Args:
            llm: Language model instance (optional)
        """
        self.llm = llm
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """
        Create and configure the Senior Auditor agent
        
        Returns:
            Agent: Configured agent instance
        """
        return Agent(
            role='Senior Auditor',
            goal='Create comprehensive and actionable audit plans for financial data analysis',
            backstory="""You are a highly experienced Senior Auditor with expertise in financial auditing 
            and risk assessment. Your role involves analyzing audit requirements, creating strategic audit 
            plans, and coordinating with IT auditors for detailed investigations. You excel at:
            - Risk assessment and prioritization
            - Compliance with auditing standards
            - Strategic planning and execution
            - Cross-functional team coordination
            - Complex data analysis planning""",
            verbose=True,
            llm=self.llm,
            max_iter=2
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
            Create a comprehensive audit plan following these steps:
            
            1. Audit Context Analysis:
               - Review the specific audit cycle and assertions
               - Identify key risk areas and focus points
               - Determine compliance requirements
            
            2. Database Schema Analysis:
               Schema for {category} category:
               {schemas}
               
               - Analyze table relationships and dependencies
               - Identify key data points for investigation
               - Map data flow between tables
            
            3. Audit Plan Development:
               - Define specific audit procedures
               - Create detailed SQL queries for data analysis
               - Set clear criteria and thresholds
               - Establish validation checkpoints
            
            Input Context:
            {problem}
            
            Guidelines:
            - Ensure queries are optimized and efficient
            - Include data validation steps
            - Consider data completeness and accuracy
            - Align with audit standards and regulations
            """,
            expected_output="Detailed audit plan with specific procedures and SQL queries, stored in 'result' variable",
            agent=self.agent,
        )