from typing import Dict, List, Optional, Any
from .senior_auditor import SeniorAuditorAgent
from .it_auditor import ITAuditorAgent
from .report_manager import AuditReportManager
from ..database.models import DatabaseManager
from ..services.dataset_service import DatasetService
from crewai import Crew

class AgentCoordinator:
    def __init__(self, db_manager: DatabaseManager, dataset_service: DatasetService, llm=None):
        self.db_manager = db_manager
        self.dataset_service = dataset_service
        self.llm = llm
        
        # Initialize agents
        self.senior_auditor = SeniorAuditorAgent(llm=self.llm)
        self.it_auditor = ITAuditorAgent(db_manager=self.db_manager, llm=self.llm)
        self.report_manager = AuditReportManager(llm=self.llm)
        
        # Initialize chat history
        self.chat_histories: Dict[str, List[Dict[str, Any]]] = {}
        self.max_history = 5
    
    def _update_chat_history(self, client_id: str, message: str, response: str):
        """Update chat history for a client, keeping only last 5 conversations"""
        if client_id not in self.chat_histories:
            self.chat_histories[client_id] = []
            
        self.chat_histories[client_id].append({
            "user": message,
            "assistant": response
        })
        
        # Keep only last 5 conversations
        if len(self.chat_histories[client_id]) > self.max_history:
            self.chat_histories[client_id] = self.chat_histories[client_id][-self.max_history:]
    
    def _get_context_string(self, client_id: str) -> str:
        """Convert chat history to context string"""
        if client_id not in self.chat_histories:
            return ""
            
        context = "Previous conversations:\n"
        for conv in self.chat_histories[client_id]:
            context += f"User: {conv['user']}\n"
            context += f"Assistant: {conv['assistant']}\n"
        return context
    
    async def execute_audit(self, audit_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the full audit process"""
        try:
            # Get client_id and message
            client_id = audit_info.get("client_id")
            message = audit_info.get("message")
            
            if not client_id:
                raise ValueError("client_id is required")

            # Get category from context
            category = audit_info.get("context", {}).get("category")
            if not category:
                raise ValueError("Category is required in the audit context")
                
            # Get table schemas for the category
            category_data = self.dataset_service.get_category_table_schemas(category)
            schemas = category_data.get("tables", {})
            
            # Get chat history context
            chat_context = self._get_context_string(client_id)
            
            # Combine message with context
            enhanced_message = f"{chat_context}\nCurrent question: {message}"
            
            # Create tasks with schema information
            interpret_task = self.senior_auditor.get_task(
                enhanced_message,
                category=category,
                schemas=schemas
            )

            it_auditor_task = self.it_auditor.get_task()

            report_manager_task = self.report_manager.get_task()

            # Create and execute crew
            crew = Crew(
                agents=[self.senior_auditor.agent, self.it_auditor.agent, self.report_manager.agent],
                tasks=[interpret_task, it_auditor_task, report_manager_task],
                max_rpm=20,
                max_tokens=4000,
                verbose=True
            )
            
            # Execute crew
            result = crew.kickoff()
            
            # Update chat history
            self._update_chat_history(client_id, message, result.raw)
            
            return result.raw
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }