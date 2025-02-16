from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
import json
import logging
from datetime import datetime
import os

from .config import settings
from .database.models import DatabaseManager
from .utils.csv_processor import CSVProcessor
from .agents.coordinator import AgentCoordinator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(**settings.api_settings)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager()
csv_processor = CSVProcessor(
    dataset_path=settings.DATASET_PATH,
    db_manager=db_manager
)
agent_coordinator = AgentCoordinator(db_manager=db_manager)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.chat_history: Dict[str, List[Dict]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        if client_id not in self.chat_history:
            self.chat_history[client_id] = []

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, websocket: WebSocket, message: Dict):
        await websocket.send_json(message)

    def add_to_history(self, client_id: str, message: Dict):
        if client_id in self.chat_history:
            self.chat_history[client_id].append({
                **message,
                "timestamp": datetime.now().isoformat()
            })

manager = ConnectionManager()

# Process initial dataset
@app.on_event("startup")
async def startup_event():
    """Initialize database and process CSV files on startup"""
    try:
        settings.validate_settings()
        csv_processor.process_csv_files()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise

# WebSocket connection for real-time chat
@app.websocket("/ws/chat/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            message = await websocket.receive_text()
            
            # Process message through agent coordinator
            try:
                request_data = json.loads(message)

                print("Audit Info: ", request_data)

                return None

                response = await agent_coordinator.execute_audit(audit_info=request_data)

                
                # Format response
                formatted_response = {
                    "type": "agent_response",
                    "timestamp": datetime.now().isoformat(),
                    "data": response
                }
                
                # Store in chat history
                manager.add_to_history(client_id, {
                    "role": "user",
                    "content": request_data.get("message")
                })
                manager.add_to_history(client_id, {
                    "role": "assistant",
                    "content": response
                })
                
                await manager.send_message(websocket, formatted_response)
                
            except json.JSONDecodeError:
                await manager.send_message(websocket, {
                    "type": "error",
                    "message": "Invalid message format"
                })
            except Exception as e:
                await manager.send_message(websocket, {
                    "type": "error",
                    "message": str(e)
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": "connected",
        "agents": await agent_coordinator.get_agent_status()
    }

@app.get("/chat/{client_id}/history")
async def get_chat_history(client_id: str):
    """Get chat history for a client"""
    return {
        "client_id": client_id,
        "history": manager.chat_history.get(client_id, [])
    }

@app.get("/tables")
async def get_tables() -> List[str]:
    """Get list of all tables in database"""
    return db_manager.get_table_names()

@app.get("/tables/{table_name}/schema")
async def get_table_schema(table_name: str) -> Dict:
    """Get schema for specific table"""
    try:
        return db_manager.get_table_schema(table_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/dataset/categories")
async def get_dataset_categories():
    """Get all dataset categories and their files"""
    return csv_processor.get_dataset_categories()

@app.get("/dataset/metadata")
async def get_dataset_metadata():
    """Get metadata about all CSV files"""
    return csv_processor.get_csv_metadata()

@app.get("/dataset/{category}/tables")
async def get_category_tables(category: str):
    """Get all tables and their schemas for a specific category"""
    # Get all categories
    categories = csv_processor.get_dataset_categories()
    
    # Check if category exists
    if category not in categories:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    # Get tables for this category
    table_schemas = {}
    for csv_file in categories[category]:
        table_name = os.path.splitext(csv_file)[0].lower()
        try:
            table_schemas[table_name] = db_manager.get_table_schema(table_name)
        except ValueError:
            # Skip tables that haven't been created yet
            continue
    
    return {
        "category": category,
        "tables": table_schemas
    }

@app.post("/dataset/sync")
async def sync_dataset():
    """Manually trigger dataset synchronization"""
    try:
        import_stats = csv_processor.process_csv_files()
        return {
            "status": "success",
            "imported_files": import_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "status": "error",
        "code": exc.status_code,
        "message": str(exc.detail)
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "status": "error",
        "code": 500,
        "message": "Internal server error"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
