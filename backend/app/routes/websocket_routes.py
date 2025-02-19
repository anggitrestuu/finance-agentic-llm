from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json
import logging
from datetime import datetime

from ..websockets.connection_manager import ConnectionManager
from ..agents.coordinator import AgentCoordinator

logger = logging.getLogger(__name__)
router = APIRouter()
manager = ConnectionManager()

def init_websocket_routes(agent_coordinator: AgentCoordinator) -> APIRouter:
    """
    Initialize WebSocket routes with dependencies
    
    Args:
        agent_coordinator: Coordinator for agent operations
        
    Returns:
        APIRouter: Router with WebSocket endpoints
    """
    
    @router.websocket("/ws/chat/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, client_id: str):
        """
        WebSocket endpoint for real-time chat
        
        Args:
            websocket: WebSocket connection
            client_id: Unique client identifier
        """
        await manager.connect(websocket, client_id)
        try:
            while True:
                message = await websocket.receive_text()
                
                try:
                    # Process message through agent coordinator
                    request_data = json.loads(message)
                    request_data["client_id"] = client_id
                    
                    logger.info(f"Processing request from client {client_id}")
                    response = await agent_coordinator.execute_audit(audit_info=request_data)
                    
                    # Format response
                    formatted_response = {
                        "type": "agent_response",
                        "timestamp": datetime.now().isoformat(),
                        "data": response.get("result"),
                        "logs": response.get("logs")
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
                    logger.error("Invalid message format received")
                    await manager.send_message(websocket, {
                        "type": "error",
                        "message": "Invalid message format"
                    })
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    await manager.send_message(websocket, {
                        "type": "error",
                        "message": str(e)
                    })
                    
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            logger.info(f"Client {client_id} disconnected")
    
    @router.get("/chat/{client_id}/history")
    async def get_chat_history(client_id: str):
        """
        Get chat history for a client
        
        Args:
            client_id: Client identifier
            
        Returns:
            Dict containing client ID and chat history
        """
        return {
            "client_id": client_id,
            "history": manager.get_client_history(client_id)
        }
    
    return router