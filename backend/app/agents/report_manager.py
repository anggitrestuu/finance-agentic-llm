from crewai import Agent, Task
from typing import Dict, Any

class AuditReportManager:
    def __init__(self, llm=None):
        self.llm = llm
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the Audit Report Manager agent with specific traits and goals"""
        return Agent(
            role='Audit Report Manager',
            goal='Create comprehensive and compelling audit reports with clear insights and recommendations',
            backstory="""You are an experienced Audit Report Manager with expertise in 
            synthesizing complex findings into clear, actionable reports. You excel at 
            communicating technical findings to various stakeholders and providing 
            strategic recommendations based on audit results.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            max_iter=1
        )
    
    def get_task(self, audit_plan: Dict[str, Any]) -> Task:
        return Task(
            description="""Using the python dataset analysis results provided by the IT Auditor Team, write an engaging and comprehensive audit report.
                Your report should be:
                - Informative and accessible to a non-technical audience.
                - Clear and concise, avoiding complex jargon to ensure readability.
                - Comprehensive, covering the audit procedures and associated audit findings.
                
                Your report should include:
                - A brief introduction that provides context for the audit.
                - A detailed description of the performed audit procedures.
                - A thorough presentation of the obtained audit findings, including payment details.
                - Actionable recommendations based on the findings.
                - A final conclusion that summarizes the key points and implications.
                
                The goal is to create a report that effectively communicates the audit findings and provides valuable insights to stakeholders. 
                As the report-writing expert, you are responsible for producing this report without requesting additional information. Utilize the provided data and insights to complete your task effectively.""",
            expected_output="A full audit report presented in a clear and accessible manner.",
            agent=self.agent,
        )