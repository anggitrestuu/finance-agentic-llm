from typing import Dict, List, Optional, Any
from .senior_auditor import SeniorAuditorAgent
from .it_auditor import ITAuditorAgent
from .report_manager import AuditReportManager
from ..database.models import DatabaseManager
from ..services.dataset_service import DatasetService
from crewai import Crew
import io
import sys
from contextlib import redirect_stdout
import asyncio
from concurrent.futures import ThreadPoolExecutor

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
        max_history: int = 5
    ):
        self.db_manager = db_manager
        self.dataset_service = dataset_service
        
        # Initialize chat history manager
        self.chat_history = ChatHistory(max_history=max_history)
        
        # Initialize thread pool for CPU-bound operations
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Initialize agents
        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """Initialize all required agents"""
        self.senior_auditor = SeniorAuditorAgent()
        self.it_auditor = ITAuditorAgent(db_manager=self.db_manager)
        self.report_manager = AuditReportManager()

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
    
    async def _run_crew_kickoff(self, crew: Crew) -> tuple[Any, str]:
        """Execute crew.kickoff() in a separate thread"""
        captured_output = io.StringIO()
        
        def run_kickoff():
            with redirect_stdout(captured_output):
                try:
                    return crew.kickoff()
                except Exception as crew_error:
                    return str(crew_error)
        
        # Run CPU-bound crew.kickoff() in thread pool
        result = await asyncio.to_thread(run_kickoff)
        return result, captured_output.getvalue()
    
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
            
            # Setup crew
            crew = self._setup_crew(enhanced_message, category, schemas)
            
            # Run crew.kickoff() asynchronously
            result, logs = await self._run_crew_kickoff(crew)
            
            # Format response
            if hasattr(result, 'raw'):
                response = result.raw
            else:
                response = str(result)
            
            # Update chat history
            self.chat_history.add_conversation(client_id, message, response)
            
            return {
                "status": "success",
                "result": response,
                "logs": logs
            }
            
        except ValueError as ve:
            return {
                "status": "error",
                "error": "Validation error",
                "error_details": str(ve),
                "logs": ""
            }
        except Exception as e:
            return {
                "status": "error",
                "error": "Unexpected error",
                "error_details": str(e),
                "logs": ""
            }