from crewai import Agent
from langchain.tools import Tool
from typing import List, Dict
import json
from datetime import datetime

class AuditReportManager:
    def __init__(self, llm=None):
        self.llm = llm
        self.agent = self._create_agent()
        self.tools = self._create_tools()

    def _create_agent(self) -> Agent:
        """Create the Audit Report Manager agent with specific traits and goals"""
        return Agent(
            role='Audit Report Manager',
            goal='Create comprehensive and compelling audit reports with clear insights and recommendations',
            backstory="""You are an experienced Audit Report Manager with expertise in 
            synthesizing complex findings into clear, actionable reports. You excel at 
            communicating technical findings to various stakeholders and providing 
            strategic recommendations based on audit results.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )

    def _create_tools(self) -> List[Tool]:
        """Create tools available to the Report Manager"""
        return [
            Tool(
                name="GenerateExecutiveSummary",
                func=self._generate_executive_summary,
                description="Create an executive summary of audit findings"
            ),
            Tool(
                name="CreateDetailedReport",
                func=self._create_detailed_report,
                description="Generate a detailed audit report with findings and recommendations"
            ),
            Tool(
                name="GenerateRecommendations",
                func=self._generate_recommendations,
                description="Create specific recommendations based on audit findings"
            )
        ]

    async def generate_report(self, 
                            category: str, 
                            audit_findings: Dict, 
                            technical_analysis: Dict) -> Dict:
        """Generate a comprehensive audit report"""
        try:
            report = {
                "report_id": f"AR{datetime.now().strftime('%Y%m%d%H%M')}",
                "category": category,
                "date": datetime.now().isoformat(),
                "executive_summary": await self._generate_executive_summary(
                    category, audit_findings
                ),
                "detailed_findings": await self._create_detailed_report(
                    audit_findings, technical_analysis
                ),
                "recommendations": await self._generate_recommendations(
                    category, audit_findings, technical_analysis
                ),
                "appendices": self._create_appendices(technical_analysis)
            }
            
            return report
        except Exception as e:
            return {
                "error": str(e),
                "category": category
            }

    async def _generate_executive_summary(self, category: str, findings: Dict) -> Dict:
        """Generate an executive summary of the audit findings"""
        summary = {
            "overview": self._create_overview(category),
            "key_findings": self._summarize_key_findings(findings),
            "risk_assessment": self._summarize_risks(findings),
            "critical_recommendations": self._get_critical_recommendations(findings)
        }
        
        return summary

    async def _create_detailed_report(self, 
                                    audit_findings: Dict, 
                                    technical_analysis: Dict) -> Dict:
        """Create a detailed audit report"""
        detailed_report = {
            "methodology": self._describe_methodology(audit_findings["category"]),
            "findings": self._format_findings(audit_findings, technical_analysis),
            "analysis": {
                "patterns": self._analyze_patterns(technical_analysis),
                "trends": self._analyze_trends(technical_analysis),
                "anomalies": self._analyze_anomalies(technical_analysis)
            },
            "supporting_evidence": self._compile_evidence(technical_analysis)
        }
        
        return detailed_report

    async def _generate_recommendations(self, 
                                     category: str, 
                                     audit_findings: Dict,
                                     technical_analysis: Dict) -> List[Dict]:
        """Generate specific recommendations based on findings"""
        recommendations = []
        
        # Process findings and generate recommendations
        risk_levels = ["High", "Medium", "Low"]
        
        for risk_level in risk_levels:
            relevant_findings = self._filter_findings_by_risk(
                audit_findings, risk_level
            )
            
            for finding in relevant_findings:
                recommendation = {
                    "risk_level": risk_level,
                    "finding_ref": finding.get("id"),
                    "recommendation": self._create_recommendation(
                        finding, technical_analysis
                    ),
                    "implementation_priority": self._determine_priority(
                        finding, risk_level
                    ),
                    "estimated_effort": self._estimate_effort(finding),
                    "expected_impact": self._assess_impact(finding)
                }
                recommendations.append(recommendation)
        
        return recommendations

    def _create_overview(self, category: str) -> str:
        """Create an overview based on the audit category"""
        overviews = {
            "Revenue": """This audit examined the revenue cycle processes, including 
                        sales transactions, customer data, and cash receipts. The review 
                        focused on accuracy, completeness, and compliance with established 
                        procedures.""",
            "Expenditure": """This audit assessed the expenditure cycle, including 
                            purchase orders, vendor payments, and inventory management. 
                            The review evaluated control effectiveness and process 
                            efficiency.""",
            "Fraud": """This audit investigated potential fraudulent activities, 
                       analyzing transaction patterns, system access, and control 
                       violations. The review focused on identifying suspicious 
                       activities and control weaknesses."""
        }
        
        return overviews.get(category, "Overview not available for this category.")

    def _summarize_key_findings(self, findings: Dict) -> List[Dict]:
        """Summarize key findings from the audit"""
        return [
            {
                "id": finding.get("id"),
                "summary": finding.get("summary"),
                "risk_level": finding.get("risk_level"),
                "impact": finding.get("impact")
            }
            for finding in findings.get("key_findings", [])
        ]

    def _summarize_risks(self, findings: Dict) -> Dict:
        """Summarize identified risks"""
        risk_summary = {
            "high_risks": [],
            "medium_risks": [],
            "low_risks": []
        }
        
        for finding in findings.get("findings", []):
            risk_level = finding.get("risk_level", "").lower()
            if risk_level in risk_summary:
                risk_summary[f"{risk_level}_risks"].append({
                    "description": finding.get("description"),
                    "potential_impact": finding.get("impact")
                })
        
        return risk_summary

    def _format_findings(self, 
                        audit_findings: Dict, 
                        technical_analysis: Dict) -> List[Dict]:
        """Format findings with technical analysis integration"""
        formatted_findings = []
        
        for finding in audit_findings.get("findings", []):
            technical_details = self._get_technical_details(
                finding, technical_analysis
            )
            
            formatted_finding = {
                "id": finding.get("id"),
                "description": finding.get("description"),
                "technical_details": technical_details,
                "risk_level": finding.get("risk_level"),
                "evidence": finding.get("evidence", []),
                "impact": finding.get("impact"),
                "affected_areas": finding.get("affected_areas", [])
            }
            formatted_findings.append(formatted_finding)
        
        return formatted_findings

    def _create_appendices(self, technical_analysis: Dict) -> Dict:
        """Create appendices with supporting technical information"""
        return {
            "statistical_analysis": technical_analysis.get("statistics", {}),
            "data_samples": technical_analysis.get("samples", []),
            "methodology_details": technical_analysis.get("methodology", {}),
            "technical_diagrams": technical_analysis.get("diagrams", [])
        }

    def _get_technical_details(self, 
                             finding: Dict, 
                             technical_analysis: Dict) -> Dict:
        """Extract relevant technical details for a finding"""
        finding_id = finding.get("id")
        return technical_analysis.get("details", {}).get(finding_id, {})

    def _filter_findings_by_risk(self, 
                               findings: Dict, 
                               risk_level: str) -> List[Dict]:
        """Filter findings by risk level"""
        return [
            finding for finding in findings.get("findings", [])
            if finding.get("risk_level") == risk_level
        ]

    def _create_recommendation(self, 
                             finding: Dict, 
                             technical_analysis: Dict) -> Dict:
        """Create a specific recommendation for a finding"""
        return {
            "action_items": self._generate_action_items(finding),
            "technical_requirements": self._get_technical_requirements(
                finding, technical_analysis
            ),
            "timeline": self._suggest_timeline(finding),
            "success_criteria": self._define_success_criteria(finding)
        }

    def _generate_action_items(self, finding: Dict) -> List[str]:
        """Generate specific action items for a recommendation"""
        # Implementation-specific logic for generating action items
        return []

    def _determine_priority(self, finding: Dict, risk_level: str) -> str:
        """Determine implementation priority"""
        # Implementation-specific logic for priority determination
        return "High"

    def _estimate_effort(self, finding: Dict) -> str:
        """Estimate implementation effort"""
        # Implementation-specific logic for effort estimation
        return "Medium"

    def _assess_impact(self, finding: Dict) -> Dict:
        """Assess expected impact of implementing recommendation"""
        return {
            "operational": "Significant improvement in process efficiency",
            "financial": "Potential cost savings",
            "risk_reduction": "High"
        }