from typing import Dict, List, Optional, Any
from .senior_auditor import SeniorAuditorAgent
from .it_auditor import ITAuditorAgent
from .report_manager import AuditReportManager
from ..database.models import DatabaseManager
from crewai import Crew

class AgentCoordinator:
    def __init__(self, db_manager: DatabaseManager, llm=None):
        self.db_manager = db_manager
        self.llm = llm
        
        # Initialize agents
        self.senior_auditor = SeniorAuditorAgent(llm=self.llm)
        self.it_auditor = ITAuditorAgent(db_manager=self.db_manager, llm=self.llm)
        self.report_manager = AuditReportManager(llm=self.llm)
    
    async def execute_audit(self, audit_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the full audit process"""
        try:
            # Create tasks
            interpret_task = self.senior_auditor.get_task(audit_info.get("message"))  # Will be updated with user query
            analyze_task = self.it_auditor.get_task()  # Will be updated with audit plan
            report_task = self.report_manager.get_task()  # Will be updated with audit findings
            
            # Create and execute crew
            crew = Crew(
                agents=[
                    self.senior_auditor.agent,
                    self.it_auditor.agent,
                    self.report_manager.agent
                ],
                tasks=[interpret_task, analyze_task, report_task],
                max_rpm=20,
                max_tokens=4000,
                verbose=True
            )
            
            # Execute crew
            result = crew.kickoff()
            
            return result.raw
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }