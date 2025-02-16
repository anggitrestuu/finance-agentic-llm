from typing import Dict
import os
from fastapi import HTTPException

from ..database.models import DatabaseManager
from ..utils.csv_processor import CSVProcessor


class DatasetService:
    def __init__(self, db_manager: DatabaseManager, csv_processor: CSVProcessor):
        self.db_manager = db_manager
        self.csv_processor = csv_processor

    def get_category_table_schemas(self, category: str) -> Dict:
        """
        Get all tables and their schemas for a specific category.
        
        Args:
            category (str): The category name to get tables for
            
        Returns:
            Dict: Dictionary containing category and its table schemas
            
        Raises:
            HTTPException: If category is not found
        """
        # Get all categories
        categories = self.csv_processor.get_dataset_categories()
        
        # Check if category exists
        if category not in categories:
            raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
        
        # Get tables for this category
        table_schemas = {}
        for csv_file in categories[category]:
            table_name = os.path.splitext(csv_file)[0].lower()
            try:
                table_schemas[table_name] = self.db_manager.get_table_schema(table_name)
            except ValueError:
                # Skip tables that haven't been created yet
                continue
        
        return {
            "category": category,
            "tables": table_schemas
        }

    def get_all_categories(self) -> Dict:
        """
        Get all dataset categories.
        
        Returns:
            Dict: Dictionary of categories and their files
        """
        return self.csv_processor.get_dataset_categories()

    def get_dataset_metadata(self) -> Dict:
        """
        Get metadata about all CSV files.
        
        Returns:
            Dict: Dictionary containing CSV metadata
        """
        return self.csv_processor.get_csv_metadata()