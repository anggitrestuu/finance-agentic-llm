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
            analyze_task = self.it_auditor.get_task({})  # Will be updated with audit plan
            report_task = self.report_manager.get_task({})  # Will be updated with audit findings
            
            # Create and execute crew
            crew = Crew(
                agents=[
                    self.senior_auditor.agent,
                    # self.it_auditor.agent,
                    # self.report_manager.agent
                ],
                tasks=[interpret_task],
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

    async def process_query(self, query: str, context: Optional[Dict] = None) -> Dict:
        """Process user query and coordinate agent responses"""
        try:
            # Analyze query to determine the appropriate workflow
            workflow = self._determine_workflow(query)
            
            if workflow["type"] == "audit_plan":
                return await self._handle_audit_plan_workflow(query, workflow, context)
            elif workflow["type"] == "data_analysis":
                return await self._handle_data_analysis_workflow(query, workflow, context)
            elif workflow["type"] == "report_generation":
                return await self._handle_report_workflow(query, workflow, context)
            else:
                return {
                    "error": "Unable to determine appropriate workflow",
                    "message": "Please provide more specific information about your audit request."
                }

        except Exception as e:
            return {
                "error": str(e),
                "message": "An error occurred while processing your request."
            }

    def _determine_workflow(self, query: str) -> Dict:
        """Determine the appropriate workflow based on the query"""
        # Simple keyword-based workflow determination
        query_lower = query.lower()
        
        workflow = {
            "type": None,
            "category": None,
            "focus_areas": []
        }
        
        # Determine category
        if "revenue" in query_lower:
            workflow["category"] = "Revenue"
        elif "expenditure" in query_lower:
            workflow["category"] = "Expenditure"
        elif "fraud" in query_lower:
            workflow["category"] = "Fraud"
            
        # Determine workflow type
        if any(word in query_lower for word in ["plan", "strategy", "approach"]):
            workflow["type"] = "audit_plan"
        elif any(word in query_lower for word in ["analyze", "check", "investigate"]):
            workflow["type"] = "data_analysis"
        elif any(word in query_lower for word in ["report", "summary", "findings"]):
            workflow["type"] = "report_generation"
            
        return workflow

    async def _handle_audit_plan_workflow(self, 
                                        query: str, 
                                        workflow: Dict, 
                                        context: Optional[Dict]) -> Dict:
        """Handle workflow for audit planning"""
        try:
            # 1. Get audit plan from Senior Auditor
            audit_scope = await self.senior_auditor.handle_query(query, {
                "category": workflow["category"],
                "context": context
            })
            
            # 2. Get initial technical assessment from IT Auditor
            technical_assessment = await self.it_auditor.analyze_data(
                workflow["category"],
                "initial_assessment"
            )
            
            return {
                "type": "audit_plan",
                "category": workflow["category"],
                "audit_scope": audit_scope,
                "technical_assessment": technical_assessment,
                "next_steps": self._generate_next_steps(audit_scope)
            }
        except Exception as e:
            return {"error": str(e)}

    async def _handle_data_analysis_workflow(self, 
                                           query: str, 
                                           workflow: Dict, 
                                           context: Optional[Dict]) -> Dict:
        """Handle workflow for data analysis"""
        try:
            # 1. Get analysis requirements from Senior Auditor
            analysis_requirements = await self.senior_auditor.handle_query(query, {
                "category": workflow["category"],
                "context": context
            })
            
            # 2. Perform technical analysis
            technical_analysis = await self.it_auditor.analyze_data(
                workflow["category"],
                analysis_requirements.get("focus_area")
            )
            
            return {
                "type": "analysis_results",
                "category": workflow["category"],
                "analysis": technical_analysis,
                "recommendations": self._format_analysis_recommendations(
                    technical_analysis
                )
            }
        except Exception as e:
            return {"error": str(e)}

    async def _handle_report_workflow(self, 
                                    query: str, 
                                    workflow: Dict, 
                                    context: Optional[Dict]) -> Dict:
        """Handle workflow for report generation"""
        try:
            # 1. Get audit findings from Senior Auditor
            audit_findings = await self.senior_auditor.handle_query(query, {
                "category": workflow["category"],
                "context": context
            })
            
            # 2. Get technical analysis from IT Auditor
            technical_analysis = await self.it_auditor.analyze_data(
                workflow["category"],
                "comprehensive"
            )
            
            # 3. Generate report
            report = await self.report_manager.generate_report(
                workflow["category"],
                audit_findings,
                technical_analysis
            )
            
            return {
                "type": "audit_report",
                "category": workflow["category"],
                "report": report
            }
        except Exception as e:
            return {"error": str(e)}

    def _generate_next_steps(self, audit_scope: Dict) -> List[str]:
        """Generate next steps based on audit scope"""
        next_steps = []
        
        if audit_scope.get("objectives"):
            for objective in audit_scope["objectives"]:
                next_steps.append(f"Plan detailed procedures for: {objective}")
                
        if audit_scope.get("key_risks"):
            for risk in audit_scope["key_risks"]:
                next_steps.append(f"Develop testing procedures for risk: {risk}")
                
        return next_steps

    def _format_analysis_recommendations(self, analysis: Dict) -> List[Dict]:
        """Format analysis recommendations"""
        recommendations = []
        
        if analysis.get("findings"):
            for finding in analysis["findings"]:
                recommendations.append({
                    "area": finding.get("area"),
                    "finding": finding.get("description"),
                    "recommendation": finding.get("recommendation"),
                    "priority": finding.get("priority", "Medium")
                })
                
        return recommendations

    async def get_agent_status(self) -> Dict:
        """Get status of all agents"""
        return {
            "senior_auditor": {
                "status": "active",
                "current_tasks": []
            },
            "it_auditor": {
                "status": "active",
                "current_tasks": []
            },
            "report_manager": {
                "status": "active",
                "current_tasks": []
            }
        }