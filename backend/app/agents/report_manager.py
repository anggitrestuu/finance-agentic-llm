from crewai import Agent, Task, LLM
from ..config import settings

class AuditReportManager:
    """
    Manages the creation and formatting of audit reports.
    
    This class is responsible for taking raw audit findings and converting them
    into well-structured, readable reports for stakeholders.
    """
    
    def __init__(self):
        """
        Initialize the Audit Report Manager
        """
        self.llm = self._setup_llm()
        self.agent = self._create_agent()
    
    def _setup_llm(self) -> LLM:
        return LLM(
            model="gpt-4o",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.4,
            max_tokens=5000
        )

    def _create_agent(self) -> Agent:
        """
        Create and configure the Audit Report Manager agent
        
        Returns:
            Agent: Configured agent instance
        """
        return Agent(
            role='Audit Report Manager',
            goal='Create comprehensive and compelling audit reports that provide clear insights and actionable recommendations.',
            backstory="""ou are a renowned Manager Auditor, celebrated for your ability to produce insightful and impactful audit reports. 
    Your reports distill complex audit findings into clear, accessible, and actionable insights, making them highly valuable to stakeholders.""",
            verbose=True,
            llm=self.llm,
            max_iter=1,
            max_rpm=10,
            cache=True
        )
    
    def get_task(self) -> Task:
        """
        Create the report generation task
        
        Returns:
            Task: Configured task for report generation
        """
        return Task(
            description="""
             Using the python dataset analysis results provided by the IT Auditor Team, write an engaging and comprehensive audit report.
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
        As the report-writing expert, you are responsible for producing this report without requesting additional information. Utilize the provided data and insights to complete your task effectively.
                """,
            expected_output="A full audit report presented in a clear and accessible manner.",
            agent=self.agent,
        )