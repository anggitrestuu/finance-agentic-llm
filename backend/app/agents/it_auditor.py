from crewai import Agent, Task
from langchain.tools import Tool
from typing import List, Dict, Any
from crewai.tools import tool
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLDatabaseTool,
)
from langchain_community.utilities.sql_database import SQLDatabase
from ..config import settings

class ITAuditorAgent:
    def __init__(self, db_manager, llm=None):
        self.llm = llm
        self.db_manager = db_manager
        self.agent = self._create_agent()
        self.tools = self._create_tools()

    def _create_agent(self) -> Agent:
        """Create the IT Auditor agent with specific traits and goals"""
        return Agent(
            role='IT Auditor',
            goal='Perform detailed technical analysis of financial data and systems',
            backstory="""You are a skilled IT Auditor specializing in data analysis and 
            system investigations. Your expertise includes database analysis, pattern 
            recognition, and technical control assessment. You work closely with the 
            Senior Auditor to provide detailed technical insights.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            tools=self._create_tools(),
            max_iter=2
        )
    
    def get_task(self, audit_plan: Dict[str, Any]) -> Task:
        return Task(
            description="""
                You need to do this in sequence:
                1. Read and understand the specific audit plan by Senior Auditor
                2. Read the SQL Query based on the provided information and audit plan
                3. Execute the SQL Query one by one
                4. Make sure to limit the output first before implementing no limit condition, to reduce token for the context window
                5. List the findings and write it for the next agent to be for the audit report
            """,
            expected_output="Analysis of the dataset to achieve the audit goal. output of the analysis should be assigned to the 'result' variable",
            agent=self.agent,
        )

    def _create_tools(self) -> List[Tool]:
        """Create tools available to the IT Auditor"""

        db = SQLDatabase.from_uri(settings.DATABASE_URL)

        @tool("list_tables")
        def list_tables() -> str:
            """List the available tables in the database"""
            return ListSQLDatabaseTool(db=db).invoke("")
        
        @tool("tables_schema")
        def tables_schema(tables: str) -> str:
            """
            Input is a comma-separated list of tables, output is the schema and sample rows
            for those tables. Be sure that the tables actually exist by calling `list_tables` first!
            Example Input: table1, table2, table3
            """
            tool = InfoSQLDatabaseTool(db=db)
            return tool.invoke(tables)
        
        @tool("execute_sql")
        def execute_sql(sql_query: str) -> str:
            """Execute a SQL query against the database. Returns the result"""
            return QuerySQLDatabaseTool(db=db).invoke(sql_query)

        return [
            list_tables,
            tables_schema,
            execute_sql
        ]