"""
Compliance report generation for Docassemble interviews.

Generates audit-ready reports with statute citations, authority verification,
and change impact analysis.
"""

import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from .comparison import GraphDiff, compare_graphs
from .graph import DependencyGraph
from .types import NodeKind

logger = logging.getLogger(__name__)


class ComplianceReport:
    """Compliance report for an interview."""
    
    def __init__(
        self,
        graph: DependencyGraph,
        interview_name: str,
        baseline_graph: Optional[DependencyGraph] = None,
    ) -> None:
        """
        Initialize compliance report.
        
        Args:
            graph: Dependency graph to analyze
            interview_name: Name of the interview
            baseline_graph: Optional baseline graph for change analysis
        """
        self.graph = graph
        self.interview_name = interview_name
        self.baseline_graph = baseline_graph
        self.generated_at = datetime.now()
        
        # Analysis results
        self.authority_mapping: Dict[str, List[str]] = defaultdict(list)
        self.missing_authorities: List[str] = []
        self.change_summary: Optional[Dict] = None
        
        self._analyze()
    
    def _analyze(self) -> None:
        """Perform compliance analysis."""
        # Map statute citations to nodes
        for node in self.graph.nodes.values():
            if node.authority:
                authorities = [a.strip() for a in node.authority.split(',')]
                for authority in authorities:
                    self.authority_mapping[authority].append(node.name)
        
        # Find nodes without authority
        for node in self.graph.nodes.values():
            if not node.authority and node.kind in (NodeKind.VARIABLE, NodeKind.RULE):
                # Derived variables and rules should have authority
                if node.source == "derived":
                    self.missing_authorities.append(node.name)
        
        # Compare with baseline if provided
        if self.baseline_graph:
            diff = compare_graphs(self.baseline_graph, self.graph)
            self.change_summary = {
                "added_nodes": len(diff.added_nodes),
                "removed_nodes": len(diff.removed_nodes),
                "changed_nodes": len(diff.changed_nodes),
                "authority_changes": len(diff.authority_changes),
                "affected_nodes": len(diff.affected_nodes),
            }
    
    def to_html(self, output_path: Optional[Path] = None) -> str:
        """
        Generate HTML compliance report.
        
        Args:
            output_path: Optional path to save HTML file
            
        Returns:
            HTML content as string
        """
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compliance Report: {self.interview_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        .metadata {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        .statute-section {{
            margin: 20px 0;
            padding: 15px;
            background: #f0f8ff;
            border-left: 4px solid #007bff;
        }}
        .statute-name {{
            font-weight: bold;
            font-size: 1.1em;
            color: #0066cc;
        }}
        .node-list {{
            list-style-type: none;
            padding-left: 20px;
        }}
        .node-item {{
            margin: 5px 0;
            padding: 5px;
            background: white;
            border-radius: 3px;
        }}
        .warning {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .change-summary {{
            background: #e7f3ff;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #007bff;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Compliance Report</h1>
        
        <div class="metadata">
            <strong>Interview:</strong> {self.interview_name}<br>
            <strong>Generated:</strong> {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}<br>
            <strong>Total Nodes:</strong> {len(self.graph.nodes)}<br>
            <strong>Total Edges:</strong> {len(self.graph.edges)}<br>
            <strong>Statute Citations:</strong> {len(self.authority_mapping)}
        </div>
"""
        
        # Change summary
        if self.change_summary:
            html += f"""
        <div class="change-summary">
            <h2>Change Summary (vs. Baseline)</h2>
            <ul>
                <li>Added Nodes: {self.change_summary['added_nodes']}</li>
                <li>Removed Nodes: {self.change_summary['removed_nodes']}</li>
                <li>Changed Nodes: {self.change_summary['changed_nodes']}</li>
                <li>Authority Changes: {self.change_summary['authority_changes']}</li>
                <li>Affected Nodes: {self.change_summary['affected_nodes']}</li>
            </ul>
        </div>
"""
        
        # Statute citations
        html += """
        <h2>Statute Citations</h2>
"""
        for statute, node_names in sorted(self.authority_mapping.items()):
            html += f"""
        <div class="statute-section">
            <div class="statute-name">{statute}</div>
            <ul class="node-list">
"""
            for node_name in sorted(node_names):
                node = self.graph.nodes.get(node_name)
                if node:
                    html += f'                <li class="node-item">{node_name} ({node.kind.value})</li>\n'
            html += """
            </ul>
        </div>
"""
        
        # Missing authorities
        if self.missing_authorities:
            html += f"""
        <div class="warning">
            <h2>Missing Authority Warnings</h2>
            <p>The following {len(self.missing_authorities)} derived variables/rules lack authority citations:</p>
            <ul>
"""
            for node_name in sorted(self.missing_authorities):
                html += f"                <li>{node_name}</li>\n"
            html += """
            </ul>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
        
        return html
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "interview_name": self.interview_name,
            "generated_at": self.generated_at.isoformat(),
            "total_nodes": len(self.graph.nodes),
            "total_edges": len(self.graph.edges),
            "authority_mapping": dict(self.authority_mapping),
            "missing_authorities": self.missing_authorities,
            "change_summary": self.change_summary,
        }


def generate_compliance_report(
    graph: DependencyGraph,
    interview_name: str,
    baseline_graph: Optional[DependencyGraph] = None,
    output_path: Optional[Path] = None,
) -> ComplianceReport:
    """
    Generate compliance report for an interview.
    
    Args:
        graph: Dependency graph to analyze
        interview_name: Name of the interview
        baseline_graph: Optional baseline graph for change analysis
        output_path: Optional path to save HTML report
        
    Returns:
        ComplianceReport object
    """
    report = ComplianceReport(graph, interview_name, baseline_graph)
    
    if output_path:
        report.to_html(output_path)
    
    return report
