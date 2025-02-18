from fastapi import WebSocket
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections and chat history"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.chat_history: Dict[str, List[Dict]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """
        Connect a new WebSocket client
        
        Args:
            websocket: WebSocket connection
            client_id: Unique client identifier
        """
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            if client_id not in self.chat_history:
                self.chat_history[client_id] = []
            logger.info(f"Client {client_id} connected")
        except Exception as e:
            logger.error(f"Error connecting client {client_id}: {str(e)}")
            raise

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Disconnect a WebSocket client
        
        Args:
            websocket: WebSocket connection to disconnect
        """
        try:
            self.active_connections.remove(websocket)
            logger.info("Client disconnected")
        except ValueError:
            logger.warning("Attempted to disconnect non-existent connection")

    async def send_message(self, websocket: WebSocket, message: Dict) -> None:
        """
        Send a message to a WebSocket client
        
        Args:
            websocket: Target WebSocket connection
            message: Message to send
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise

    def add_to_history(self, client_id: str, message: Dict) -> None:
        """
        Add a message to client's chat history
        
        Args:
            client_id: Client identifier
            message: Message to store
        """
        if client_id in self.chat_history:
            self.chat_history[client_id].append({
                **message,
                "timestamp": datetime.now().isoformat()
            })

    def get_client_history(self, client_id: str) -> List[Dict]:
        """
        Get chat history for a specific client
        
        Args:
            client_id: Client identifier
        
        Returns:
            List of chat messages for the client
        """
        return self.chat_history.get(client_id, [])