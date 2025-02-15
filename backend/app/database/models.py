from sqlalchemy import create_engine, Column, String, Float, Integer, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from typing import Dict, Any, List
import os

# Initialize SQLAlchemy components
Base = declarative_base()
metadata = MetaData()

class DatabaseManager:
    def __init__(self, db_path: str = "finance_audit.db"):
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.metadata = metadata
        self.table_models: Dict[str, Any] = {}

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def create_table_from_csv(self, csv_path: str) -> str:
        """Create a database table dynamically from CSV structure"""
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Generate table name from file path
        table_name = os.path.splitext(os.path.basename(csv_path))[0].lower()
        
        # Create column definitions starting with id as primary key
        columns = [
            Column('id', Integer, primary_key=True, autoincrement=True)
        ]
        
        for col in df.columns:
            col_name = col.strip().lower().replace(' ', '_')
            col_type = self._infer_column_type(df[col])
            columns.append(Column(col_name, col_type))

        # Create unique class name to avoid conflicts
        class_name = f"{table_name}_table"
        
        # Create dynamic table class
        table_class = type(
            class_name,
            (Base,),
            {
                '__tablename__': table_name,
                '__table_args__': {'extend_existing': True},
                **{col.name: col for col in columns}
            }
        )

        # Store model reference
        self.table_models[table_name] = table_class
        
        # Create table in database
        table_class.__table__.create(bind=self.engine, checkfirst=True)
        
        return table_name

    def _infer_column_type(self, series: pd.Series) -> Any:
        """Infer SQLAlchemy column type from pandas series"""
        dtype = series.dtype
        
        if pd.api.types.is_integer_dtype(dtype):
            return Integer
        elif pd.api.types.is_float_dtype(dtype):
            return Float
        else:
            return String

    def import_csv_data(self, csv_path: str) -> int:
        """Import CSV data into corresponding table"""
        df = pd.read_csv(csv_path)
        table_name = os.path.splitext(os.path.basename(csv_path))[0].lower()
        
        # Clean column names
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        
        # Convert DataFrame to dict for SQLAlchemy
        records = df.to_dict('records')
        
        if table_name not in self.table_models:
            self.create_table_from_csv(csv_path)
        
        # Insert data
        with self.SessionLocal() as session:
            for record in records:
                table_model = self.table_models[table_name]
                session.add(table_model(**record))
            session.commit()
        
        return len(records)

    def get_table_names(self) -> List[str]:
        """Get list of all tables in database"""
        return list(self.table_models.keys())

    def get_table_schema(self, table_name: str) -> Dict[str, str]:
        """Get schema information for a specific table"""
        if table_name not in self.table_models:
            raise ValueError(f"Table {table_name} not found")
            
        table_model = self.table_models[table_name]
        return {
            column.name: str(column.type)
            for column in table_model.__table__.columns
        }

    def recreate_database(self):
        """Drop and recreate all tables"""
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)