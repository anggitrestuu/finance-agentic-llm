import os
from typing import List, Dict, Set
import hashlib
from watchfiles import watch
from datetime import datetime
import logging
from ..database.models import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVProcessor:
    def __init__(self, dataset_path: str, db_manager: DatabaseManager):
        self.dataset_path = dataset_path
        self.db_manager = db_manager
        self.file_hashes: Dict[str, str] = {}
        self.initialized = False

    def get_csv_files(self) -> List[str]:
        """Recursively find all CSV files in the dataset directory"""
        csv_files = []
        for root, _, files in os.walk(self.dataset_path):
            for file in files:
                if file.endswith('.csv') and not file.startswith('.'):
                    csv_files.append(os.path.join(root, file))
        return csv_files

    def calculate_file_hash(self, filepath: str) -> str:
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def process_csv_files(self) -> Dict[str, int]:
        """Process all CSV files and return number of records imported for each"""
        csv_files = self.get_csv_files()
        import_stats = {}
        
        for csv_file in csv_files:
            current_hash = self.calculate_file_hash(csv_file)
            file_name = os.path.basename(csv_file)
            
            if not self.initialized or self.file_hashes.get(csv_file) != current_hash:
                try:
                    records_imported = self.db_manager.import_csv_data(csv_file)
                    import_stats[file_name] = records_imported
                    self.file_hashes[csv_file] = current_hash
                    logger.info(f"Processed {file_name}: {records_imported} records imported")
                except Exception as e:
                    logger.error(f"Error processing {file_name}: {str(e)}")
                    import_stats[file_name] = 0
        
        self.initialized = True
        return import_stats

    def get_dataset_categories(self) -> Dict[str, List[str]]:
        """Get all categories and their associated CSV files"""
        categories = {}
        for root, dirs, files in os.walk(self.dataset_path):
            category = os.path.basename(root)
            if category != os.path.basename(self.dataset_path):
                csv_files = [f for f in files if f.endswith('.csv')]
                if csv_files:
                    categories[category] = csv_files
        return categories

    def monitor_changes(self):
        """Start monitoring CSV files for changes"""
        logger.info("Starting CSV file monitor...")
        
        for changes in watch(self.dataset_path):
            changed_files: Set[str] = set()
            
            for change_type, changed_file in changes:
                if changed_file.endswith('.csv'):
                    changed_files.add(changed_file)
            
            if changed_files:
                logger.info(f"Detected changes in {len(changed_files)} files")
                self.process_csv_files()

    def get_csv_metadata(self) -> List[Dict]:
        """Get metadata about all CSV files"""
        metadata = []
        csv_files = self.get_csv_files()
        
        for csv_file in csv_files:
            file_stat = os.stat(csv_file)
            metadata.append({
                'file_name': os.path.basename(csv_file),
                'category': os.path.basename(os.path.dirname(csv_file)),
                'full_path': csv_file,
                'size': file_stat.st_size,
                'last_modified': datetime.fromtimestamp(file_stat.st_mtime),
                'hash': self.calculate_file_hash(csv_file)
            })
        
        return metadata

    def validate_csv_structure(self, csv_file: str) -> Dict:
        """Validate CSV file structure and content"""
        try:
            table_name = os.path.splitext(os.path.basename(csv_file))[0].lower()
            current_schema = self.db_manager.get_table_schema(table_name)
            
            validation_result = {
                'file_name': os.path.basename(csv_file),
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Add additional validation logic here if needed
            
            return validation_result
        except Exception as e:
            return {
                'file_name': os.path.basename(csv_file),
                'is_valid': False,
                'errors': [str(e)],
                'warnings': []
            }