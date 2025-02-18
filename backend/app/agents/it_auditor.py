from typing import List, Dict, Any, Optional
from crewai import Agent, Task
from langchain.tools import Tool
from crewai.tools import tool
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLDatabaseTool,
)
from langchain_community.utilities.sql_database import SQLDatabase
from ..config import settings

class DatabaseTools:
    """Collection of database interaction tools"""
    
    def __init__(self, database_url: str):
        self.db = SQLDatabase.from_uri(database_url)
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize and return all database tools"""
        
        @tool("list_tables")
        def list_tables() -> str:
            """List all available tables in the database"""
            try:
                return ListSQLDatabaseTool(db=self.db).invoke("")
            except Exception as e:
                return f"Error listing tables: {str(e)}"
        
        @tool("tables_schema")
        def tables_schema(tables: str) -> str:
            """
            Get schema and sample rows for specified tables.
            
            Args:
                tables: Comma-separated list of table names
                
            Returns:
                Schema information and sample data for the specified tables
            """
            try:
                return InfoSQLDatabaseTool(db=self.db).invoke(tables)
            except Exception as e:
                return f"Error getting schema for tables {tables}: {str(e)}"
        
        @tool("execute_sql")
        def execute_sql(sql_query: str) -> str:
            """
            Execute SQL query and return results
            
            Args:
                sql_query: Valid SQL query to execute
                
            Returns:
                Query results or error message if query fails
            """
            try:
                return QuerySQLDatabaseTool(db=self.db).invoke(sql_query)
            except Exception as e:
                return f"Error executing query: {str(e)}\nQuery: {sql_query}"
        
        return [
            list_tables,
            tables_schema,
            execute_sql
        ]

class ITAuditorAgent:
    """Agent responsible for technical analysis of financial data"""
    
    def __init__(self, db_manager: Any, llm: Optional[Any] = None):
        """
        Initialize IT Auditor agent
        
        Args:
            db_manager: Database manager instance
            llm: Language model instance (optional)
        """
        self.llm = llm
        self.db_manager = db_manager
        self.db_tools = DatabaseTools(settings.DATABASE_URL)
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create and configure the IT Auditor agent"""
        return Agent(
            role='IT Auditor',
            goal='Perform detailed technical analysis of financial data and systems',
            backstory="""You are a skilled IT Auditor specializing in data analysis and 
            system investigations. Your expertise includes database analysis, pattern 
            recognition, and technical control assessment. You are well-versed in understanding
            database schemas and relationships between tables for different audit categories.
            You work closely with the Senior Auditor to provide detailed technical insights.""",
            verbose=True,
            llm=self.llm,
            tools=self.db_tools.tools,
            max_iter=5
        )
    
    def get_task(self) -> Task:
        """Create and return the IT Auditor's task"""
        return Task(
            description="""
                Follow these steps sequentially:
                1. Review and understand the Senior Auditor's audit plan
                2. Analyze the database schema for the given audit category
                3. Validate and verify the proposed SQL queries
                4. Execute queries with appropriate limits for testing
                5. Remove limits for final execution if results are valid
                6. Analyze results considering data relationships
                7. Document findings for the audit report
                
                Important considerations:
                - Always test queries with limits first
                - Validate data integrity across related tables
                - Document any anomalies or patterns found
                - Prepare clear, structured output for reporting
            """,
            expected_output="Comprehensive analysis results stored in the 'result' variable",
            agent=self.agent,
        )