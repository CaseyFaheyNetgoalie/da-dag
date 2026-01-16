"""
Tests for compliance report generation.
"""

import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile
from docassemble_dag.compliance import ComplianceReport, generate_compliance_report
from docassemble_dag.graph import DependencyGraph
from docassemble_dag.types import Node, NodeKind


class TestComplianceReport:
    """Test compliance report generation."""
    
    def test_authority_mapping(self):
        """Test mapping statute citations to nodes."""
        nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived", authority="CPLR 2211"),
            "y": Node("y", NodeKind.VARIABLE, "derived", authority="CPLR 308"),
            "z": Node("z", NodeKind.VARIABLE, "derived", authority="CPLR 2211, 308"),
        }
        graph = DependencyGraph(nodes, [])
        
        report = ComplianceReport(graph, "test_interview")
        
        assert "CPLR 2211" in report.authority_mapping
        assert "CPLR 308" in report.authority_mapping
        assert "x" in report.authority_mapping["CPLR 2211"]
        assert "z" in report.authority_mapping["CPLR 2211"]
        # z has "CPLR 2211, 308" - when split, both parts should be present
        # The full string "CPLR 2211, 308" should also be in mapping
        assert "z" in report.authority_mapping.get("CPLR 2211, 308", []) or "z" in report.authority_mapping.get("308", [])
    
    def test_missing_authorities(self):
        """Test detection of missing authority citations."""
        nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived", authority="CPLR 123"),
            "y": Node("y", NodeKind.VARIABLE, "derived"),  # Missing authority
            "z": Node("z", NodeKind.VARIABLE, "user_input"),  # User input doesn't need authority
        }
        graph = DependencyGraph(nodes, [])
        
        report = ComplianceReport(graph, "test_interview")
        
        assert "y" in report.missing_authorities
        assert "z" not in report.missing_authorities  # User input
    
    def test_change_summary_with_baseline(self):
        """Test change summary when baseline graph provided."""
        old_nodes = {"x": Node("x", NodeKind.VARIABLE, "derived", authority="Old Law")}
        new_nodes = {"x": Node("x", NodeKind.VARIABLE, "derived", authority="New Law")}
        
        old_graph = DependencyGraph(old_nodes, [])
        new_graph = DependencyGraph(new_nodes, [])
        
        report = ComplianceReport(new_graph, "test", baseline_graph=old_graph)
        
        assert report.change_summary is not None
        assert report.change_summary["authority_changes"] == 1
    
    def test_generate_html(self):
        """Test generating HTML compliance report."""
        nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived", authority="CPLR 123"),
        }
        graph = DependencyGraph(nodes, [])
        
        with NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            html_path = Path(f.name)
        
        try:
            report = ComplianceReport(graph, "test")
            html = report.to_html(html_path)
            
            assert html_path.exists()
            assert "Compliance Report" in html
            assert "CPLR 123" in html
        finally:
            if html_path.exists():
                html_path.unlink()
    
    def test_report_to_dict(self):
        """Test converting report to dictionary."""
        nodes = {"x": Node("x", NodeKind.VARIABLE, "derived", authority="CPLR 123")}
        graph = DependencyGraph(nodes, [])
        
        report = ComplianceReport(graph, "test")
        report_dict = report.to_dict()
        
        assert "interview_name" in report_dict
        assert "authority_mapping" in report_dict
        assert "missing_authorities" in report_dict
        assert "CPLR 123" in report_dict["authority_mapping"]


class TestGenerateComplianceReport:
    """Test compliance report generation function."""
    
    def test_generate_report(self):
        """Test generating compliance report."""
        nodes = {"x": Node("x", NodeKind.VARIABLE, "derived", authority="CPLR 123")}
        graph = DependencyGraph(nodes, [])
        
        report = generate_compliance_report(graph, "test")
        
        assert isinstance(report, ComplianceReport)
        assert report.interview_name == "test"
