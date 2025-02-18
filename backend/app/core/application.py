from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Optional

from ..config import settings
from ..database.models import DatabaseManager
from ..utils.csv_processor import CSVProcessor
from ..services.dataset_service import DatasetService
from ..agents.coordinator import AgentCoordinator
from ..routes.api_routes import APIRoutes
from ..routes.websocket_routes import init_websocket_routes
from .error_handlers import add_error_handlers

logger = logging.getLogger(__name__)

class ApplicationFactory:
    """Factory for creating and configuring the FastAPI application"""

    @staticmethod
    def create_app() -> FastAPI:
        """
        Create and configure the FastAPI application
        
        Returns:
            FastAPI: Configured application instance
        """
        # Initialize FastAPI app
        app = FastAPI(**settings.api_settings)
        
        # Configure CORS
        ApplicationFactory._setup_cors(app)
        
        # Initialize components
        components = ApplicationFactory._initialize_components()
        
        # Add routes
        ApplicationFactory._setup_routes(app, components)
        
        # Add error handlers
        add_error_handlers(app)
        
        # Add startup event
        ApplicationFactory._setup_startup_event(app, components)
        
        return app

    @staticmethod
    def _setup_cors(app: FastAPI) -> None:
        """Configure CORS middleware"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins="*",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @staticmethod
    def _initialize_components() -> dict:
        """Initialize application components"""
        try:
            db_manager = DatabaseManager()
            csv_processor = CSVProcessor(
                dataset_path=settings.DATASET_PATH,
                db_manager=db_manager
            )
            dataset_service = DatasetService(
                db_manager=db_manager,
                csv_processor=csv_processor
            )
            agent_coordinator = AgentCoordinator(
                db_manager=db_manager,
                dataset_service=dataset_service
            )
            
            return {
                "db_manager": db_manager,
                "csv_processor": csv_processor,
                "dataset_service": dataset_service,
                "agent_coordinator": agent_coordinator
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {str(e)}")
            raise

    @staticmethod
    def _setup_routes(app: FastAPI, components: dict) -> None:
        """Setup application routes"""
        try:
            # API routes
            api_routes = APIRoutes(
                dataset_service=components["dataset_service"],
                db_manager=components["db_manager"],
                csv_processor=components["csv_processor"]
            )
            app.include_router(api_routes.get_router())
            
            # WebSocket routes
            websocket_router = init_websocket_routes(
                agent_coordinator=components["agent_coordinator"]
            )
            app.include_router(websocket_router)
            
        except Exception as e:
            logger.error(f"Failed to setup routes: {str(e)}")
            raise

    @staticmethod
    def _setup_startup_event(app: FastAPI, components: dict) -> None:
        """Configure startup event"""
        @app.on_event("startup")
        async def startup_event():
            """Initialize database and process CSV files on startup"""
            try:
                settings.validate_settings()
                components["csv_processor"].process_csv_files()
                logger.info("Application started successfully")
            except Exception as e:
                logger.error(f"Startup error: {str(e)}")
                raise