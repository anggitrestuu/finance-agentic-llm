from typing import Dict, List, Optional, Any
from .senior_auditor import SeniorAuditorAgent
from .it_auditor import ITAuditorAgent
from .report_manager import AuditReportManager
from ..database.models import DatabaseManager
from ..services.dataset_service import DatasetService
from crewai import Crew

class ChatHistory:
    """Manages chat history for multiple clients"""
    def __init__(self, max_history: int = 5):
        self.histories: Dict[str, List[Dict[str, Any]]] = {}
        self.max_history = max_history
    
    def add_conversation(self, client_id: str, message: str, response: str) -> None:
        """Add a conversation to client's history"""
        if client_id not in self.histories:
            self.histories[client_id] = []
            
        self.histories[client_id].append({
            "user": message,
            "assistant": response
        })
        
        # Keep only last N conversations
        if len(self.histories[client_id]) > self.max_history:
            self.histories[client_id] = self.histories[client_id][-self.max_history:]
    
    def get_context(self, client_id: str) -> str:
        """Get formatted chat history context for a client"""
        if client_id not in self.histories:
            return ""
            
        context = "Previous conversations:\n"
        for conv in self.histories[client_id]:
            context += f"User: {conv['user']}\n"
            context += f"Assistant: {conv['assistant']}\n"
        return context

class AgentCoordinator:
    """Coordinates multiple agents to execute audit processes"""
    
    def __init__(
        self, 
        db_manager: DatabaseManager, 
        dataset_service: DatasetService, 
        llm: Optional[Any] = None,
        max_history: int = 5
    ):
        self.db_manager = db_manager
        self.dataset_service = dataset_service
        self.llm = llm
        
        # Initialize chat history manager
        self.chat_history = ChatHistory(max_history=max_history)
        
        # Initialize agents
        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """Initialize all required agents"""
        self.senior_auditor = SeniorAuditorAgent(llm=self.llm)
        self.it_auditor = ITAuditorAgent(db_manager=self.db_manager, llm=self.llm)
        self.report_manager = AuditReportManager(llm=self.llm)

    def _validate_audit_info(self, audit_info: Dict[str, Any]) -> None:
        """Validate required audit information"""
        if not audit_info.get("client_id"):
            raise ValueError("client_id is required")

        category = audit_info.get("context", {}).get("category")
        if not category:
            raise ValueError("Category is required in the audit context")

    def _setup_crew(self, enhanced_message: str, category: str, schemas: Dict[str, Any]) -> Crew:
        """Setup and configure the crew with tasks"""
        # Create tasks with schema information
        interpret_task = self.senior_auditor.get_task(
            enhanced_message,
            category=category,
            schemas=schemas
        )
        it_auditor_task = self.it_auditor.get_task()
        report_manager_task = self.report_manager.get_task()

        # Create crew with configured tasks
        return Crew(
            agents=[
                self.senior_auditor.agent, 
                self.it_auditor.agent, 
                self.report_manager.agent
            ],
            tasks=[
                interpret_task, 
                it_auditor_task, 
                report_manager_task
            ],
            max_rpm=20,
            max_tokens=4000,
            verbose=True
        )
    
    async def execute_audit(self, audit_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the full audit process with proper error handling"""
        try:
            # Validate audit information
            self._validate_audit_info(audit_info)
            
            client_id = audit_info["client_id"]
            message = audit_info.get("message", "")
            category = audit_info["context"]["category"]
            
            # Get table schemas for the category
            category_data = self.dataset_service.get_category_table_schemas(category)
            schemas = category_data.get("tables", {})
            
            # Enhanced message with chat context
            chat_context = self.chat_history.get_context(client_id)
            enhanced_message = f"{chat_context}\nCurrent question: {message}"
            
            # Setup and execute crew
            crew = self._setup_crew(enhanced_message, category, schemas)
            result = crew.kickoff()
            
            # Update chat history with new conversation
            self.chat_history.add_conversation(client_id, message, result.raw)
            
            return result.raw
            
        except ValueError as ve:
            return {
                "status": "error",
                "error": f"Validation error: {str(ve)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}"
            }