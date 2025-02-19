from typing import List, Any
from crewai import LLM, Agent, Task
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
    
    def __init__(self, db_manager: Any):
        """
        Initialize IT Auditor agent
        
        Args:
            db_manager: Database manager instance
        """
        self.llm = self._setup_llm()
        self.db_manager = db_manager
        self.db_tools = DatabaseTools(settings.DATABASE_URL)
        self.agent = self._create_agent()
    
    def _setup_llm(self) -> LLM:
        return LLM(
            model="gpt-4o",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.4,
            max_tokens=5000
        )

    def _create_agent(self) -> Agent:
        """Create and configure the IT Auditor agent"""
        return Agent(
            role='IT Auditor',
            goal='Given the information provided by Senior Auditor, analyze the targeted dataset to achieve the audit goal.',
            backstory="""You are a senior Senior IT Auditor with extensive experience in software and its best practices.
            	You have expertise in analyzing dataset given the criteria and goals using SQL Query""",
            verbose=True,
            llm=self.llm,
            tools=self.db_tools.tools,
            max_iter=8,
            max_rpm=20,
            max_tokens=4000,
            cache=True
        )
    
    def get_task(self) -> Task:
        """Create and return the IT Auditor's task"""
        return Task(
            description="""
                You need to do this in sequence:
                    1. Read and understand the specific audit plan by Senior Auditor
                    2. Read the SQL Query based on the provided information and audit plan
                    3. Execute the SQL Query one by one
                    4. Make sure to limit the output first before implementing no limit condition, to reduce token for the context window
                    5. List the findings and write it for the next agent to be for the audit report
            """,
            expected_output="Analysis of the dataset to achieve the audit goal. output of the analysis should be assigned to the 'result' variable.",
            agent=self.agent,
        )