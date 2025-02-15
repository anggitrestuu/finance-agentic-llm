from crewai import Agent
from langchain.tools import Tool
from typing import List, Dict
from sqlalchemy import text
import pandas as pd
import json

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
            llm=self.llm
        )

    def _create_tools(self) -> List[Tool]:
        """Create tools available to the IT Auditor"""
        return [
            Tool(
                name="AnalyzeTransactions",
                func=self._analyze_transactions,
                description="Analyze transaction patterns and anomalies in the dataset"
            ),
            Tool(
                name="VerifyDataIntegrity",
                func=self._verify_data_integrity,
                description="Check data consistency and integrity across tables"
            ),
            Tool(
                name="DetectAnomalies",
                func=self._detect_anomalies,
                description="Identify unusual patterns or potential issues in the data"
            )
        ]

    async def analyze_data(self, category: str, focus_area: str) -> Dict:
        """Perform comprehensive data analysis based on category and focus area"""
        analysis_results = {
            "category": category,
            "focus_area": focus_area,
            "findings": [],
            "anomalies": [],
            "metrics": {}
        }

        try:
            if category == "Revenue":
                await self._analyze_revenue_cycle(analysis_results)
            elif category == "Expenditure":
                await self._analyze_expenditure_cycle(analysis_results)
            elif category == "Fraud":
                await self._analyze_fraud_indicators(analysis_results)
            
            return analysis_results
        except Exception as e:
            return {
                "error": str(e),
                "category": category,
                "focus_area": focus_area
            }

    async def _analyze_revenue_cycle(self, results: Dict):
        """Analyze revenue cycle data"""
        with self.db_manager.SessionLocal() as session:
            # Analyze sales invoices
            sales_query = text("""
                SELECT 
                    strftime('%Y-%m', date) as month,
                    COUNT(*) as transaction_count,
                    SUM(amount) as total_amount
                FROM sales_invoice
                GROUP BY month
                ORDER BY month
            """)
            sales_data = session.execute(sales_query).fetchall()
            
            # Add sales analysis to results
            results["metrics"]["monthly_sales"] = [
                {"month": row[0], "count": row[1], "amount": row[2]}
                for row in sales_data
            ]

            # Add more revenue cycle analysis as needed

    async def _analyze_expenditure_cycle(self, results: Dict):
        """Analyze expenditure cycle data"""
        with self.db_manager.SessionLocal() as session:
            # Analyze purchase orders
            po_query = text("""
                SELECT 
                    strftime('%Y-%m', date) as month,
                    COUNT(*) as po_count,
                    SUM(ext_cost) as total_cost
                FROM purchase_order
                GROUP BY month
                ORDER BY month
            """)
            po_data = session.execute(po_query).fetchall()
            
            # Add purchase order analysis to results
            results["metrics"]["monthly_purchases"] = [
                {"month": row[0], "count": row[1], "amount": row[2]}
                for row in po_data
            ]

            # Add more expenditure cycle analysis as needed

    async def _analyze_fraud_indicators(self, results: Dict):
        """Analyze potential fraud indicators"""
        with self.db_manager.SessionLocal() as session:
            # Example: Detect unusual patterns in transactions
            unusual_patterns = text("""
                SELECT 
                    t.*,
                    'Unusual amount' as anomaly_type
                FROM (
                    SELECT *,
                        AVG(amount) OVER (PARTITION BY transaction_type) as avg_amount,
                        STDDEV(amount) OVER (PARTITION BY transaction_type) as stddev_amount
                    FROM transactions
                ) t
                WHERE ABS(t.amount - t.avg_amount) > 2 * t.stddev_amount
            """)
            
            # Add fraud analysis results
            results["anomalies"].extend([
                {
                    "type": "unusual_transaction",
                    "details": row
                } for row in session.execute(unusual_patterns).fetchall()
            ])

    def _analyze_transactions(self, table_name: str, criteria: Dict = None) -> Dict:
        """Analyze transactions based on specified criteria"""
        try:
            with self.db_manager.SessionLocal() as session:
                # Build dynamic query based on criteria
                query = f"SELECT * FROM {table_name}"
                if criteria:
                    conditions = " AND ".join(
                        f"{k} = :{k}" for k in criteria.keys()
                    )
                    query += f" WHERE {conditions}"
                
                result = session.execute(text(query), criteria or {})
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                
                return {
                    "record_count": len(df),
                    "summary_statistics": json.loads(df.describe().to_json()),
                    "potential_issues": self._identify_potential_issues(df)
                }
        except Exception as e:
            return {"error": str(e)}

    def _verify_data_integrity(self, tables: List[str]) -> Dict:
        """Verify data integrity across specified tables"""
        integrity_results = {
            "checked_tables": tables,
            "issues_found": [],
            "relationships_verified": []
        }
        
        try:
            for table in tables:
                # Verify primary key integrity
                # Check for referential integrity
                # Validate data consistency
                pass
                
            return integrity_results
        except Exception as e:
            return {"error": str(e)}

    def _detect_anomalies(self, data: Dict) -> Dict:
        """Detect anomalies in the provided dataset"""
        anomalies = {
            "statistical_outliers": [],
            "pattern_anomalies": [],
            "sequence_anomalies": []
        }
        
        # Implement anomaly detection logic
        # This could include statistical analysis, pattern recognition, etc.
        
        return anomalies

    def _identify_potential_issues(self, df: pd.DataFrame) -> List[Dict]:
        """Identify potential issues in the dataset"""
        issues = []
        
        # Check for missing values
        missing_values = df.isnull().sum()
        if missing_values.any():
            issues.append({
                "type": "missing_values",
                "details": json.loads(missing_values[missing_values > 0].to_json())
            })
        
        # Add more issue detection logic as needed
        
        return issues