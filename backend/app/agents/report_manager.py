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
            model="groq/llama3-8b-8192",
            api_key=settings.GROQ_API_KEY,
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
            goal='Create comprehensive and compelling audit reports with clear insights and recommendations',
            backstory="""You are an experienced Audit Report Manager with expertise in 
            synthesizing complex findings into clear, actionable reports. You excel at 
            communicating technical findings to various stakeholders and providing 
            strategic recommendations based on audit results. Your reports bridge the gap
            between technical details and business implications.""",
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
                Transform the technical audit findings into a clear, comprehensive report.
                
                Report Requirements:
                1. Executive Summary:
                   - Brief overview of audit scope
                   - Key findings and recommendations
                   - Overall risk assessment
                
                2. Detailed Findings:
                   - Technical analysis results
                   - Data anomalies and patterns
                   - Supporting evidence and metrics
                
                3. Recommendations:
                   - Actionable steps for improvement
                   - Priority levels for each recommendation
                   - Implementation considerations
                
                4. Conclusion:
                   - Summary of critical points
                   - Next steps and follow-up items
                
                Guidelines:
                - Use clear, non-technical language
                - Include relevant data visualizations
                - Prioritize findings by business impact
                - Provide context for technical findings
                - Focus on actionable insights
                """,
            expected_output="A comprehensive audit report formatted for clarity and impact",
            agent=self.agent,
        )