from fastapi import APIRouter, HTTPException
from typing import Dict, List
import logging

from ..services.dataset_service import DatasetService
from ..database.models import DatabaseManager
from ..utils.csv_processor import CSVProcessor

logger = logging.getLogger(__name__)
router = APIRouter()

class APIRoutes:
    """Handles API routes for dataset and table operations"""
    
    def __init__(
        self,
        dataset_service: DatasetService,
        db_manager: DatabaseManager,
        csv_processor: CSVProcessor
    ):
        """
        Initialize API routes with required services
        
        Args:
            dataset_service: Service for dataset operations
            db_manager: Database management service
            csv_processor: CSV file processor
        """
        self.dataset_service = dataset_service
        self.db_manager = db_manager
        self.csv_processor = csv_processor
        self.router = self._create_router()
    
    def _create_router(self) -> APIRouter:
        """Create and configure the API router with all routes"""
        router = APIRouter(prefix="/api")
        
        @router.get("/health")
        async def health_check():
            """Health check endpoint"""
            try:
                return {
                    "status": "healthy",
                    "database": "connected" if self.db_manager.is_connected() else "disconnected",
                    "dataset_service": "ready"
                }
            except Exception as e:
                logger.error(f"Health check failed: {str(e)}")
                raise HTTPException(status_code=500, detail="Service health check failed")
        
        @router.get("/tables", response_model=List[str])
        async def get_tables() -> List[str]:
            """Get list of all tables in database"""
            try:
                return self.db_manager.get_table_names()
            except Exception as e:
                logger.error(f"Error getting tables: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to retrieve tables")
        
        @router.get("/tables/{table_name}/schema")
        async def get_table_schema(table_name: str) -> Dict:
            """
            Get schema for specific table
            
            Args:
                table_name: Name of the table
            
            Returns:
                Dict containing table schema
            """
            try:
                return self.db_manager.get_table_schema(table_name)
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                logger.error(f"Error getting schema for {table_name}: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to retrieve schema")
        
        @router.get("/dataset/categories")
        async def get_dataset_categories():
            """Get all dataset categories and their files"""
            try:
                return self.dataset_service.get_all_categories()
            except Exception as e:
                logger.error(f"Error getting categories: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to retrieve categories")
        
        @router.get("/dataset/metadata")
        async def get_dataset_metadata():
            """Get metadata about all CSV files"""
            try:
                return self.dataset_service.get_dataset_metadata()
            except Exception as e:
                logger.error(f"Error getting metadata: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to retrieve metadata")
        
        @router.get("/dataset/{category}/tables")
        async def get_category_tables(category: str):
            """
            Get all tables and their schemas for a specific category
            
            Args:
                category: Dataset category
            
            Returns:
                Dict containing category tables and schemas
            """
            try:
                return self.dataset_service.get_category_table_schemas(category)
            except Exception as e:
                logger.error(f"Error getting tables for category {category}: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to retrieve tables for category {category}"
                )
        
        @router.post("/dataset/sync")
        async def sync_dataset():
            """Manually trigger dataset synchronization"""
            try:
                import_stats = self.csv_processor.process_csv_files()
                return {
                    "status": "success",
                    "imported_files": import_stats
                }
            except Exception as e:
                logger.error(f"Error syncing dataset: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to sync dataset")
        
        return router
    
    def get_router(self) -> APIRouter:
        """Get the configured API router"""
        return self.router