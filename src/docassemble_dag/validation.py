"""
Graph validation and policy checking.

Similar to GUAC's policy enforcement, this module provides configurable
policy rules to validate dependency graphs and detect issues.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .graph import DependencyGraph
from .types import NodeKind


class PolicySeverity(Enum):
    """Severity level for policy violations."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class PolicyViolation:
    """
    Represents a policy violation found during validation.
    
    Includes provenance information for debugging and governance.
    """
    rule_name: str
    severity: PolicySeverity
    message: str
    node_name: Optional[str] = None
    edge_info: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary for JSON serialization."""
        result = {
            "rule": self.rule_name,
            "severity": self.severity.value,
            "message": self.message
        }
        if self.node_name:
            result["node"] = self.node_name
        if self.edge_info:
            result["edge"] = self.edge_info
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class GraphValidator:
    """
    Validates dependency graphs against configurable policy rules.
    
    Similar to GUAC's policy engine, this provides rule-based validation
    with provenance tracking for violations.
    """
    
    def __init__(self, graph: DependencyGraph) -> None:
        """
        Initialize validator with a dependency graph.
        
        Args:
            graph: DependencyGraph to validate
            
        Raises:
            TypeError: If graph is not a DependencyGraph instance
        """
        if not isinstance(graph, DependencyGraph):
            raise TypeError(
                f"graph must be a DependencyGraph instance, "
                f"got {type(graph).__name__}"
            )
        self.graph = graph
        self.violations: List[PolicyViolation] = []
    
    def validate_all(self, policies: Optional[List[str]] = None) -> List[PolicyViolation]:
        """
        Run all validation policies (or specified subset).
        
        Args:
            policies: Optional list of policy names to run. If None, runs all.
        
        Returns:
            List of PolicyViolation objects
        """
        self.violations = []
        
        # Available policies
        all_policies = {
            "no_cycles": self.check_no_cycles,
            "no_orphans": self.check_no_orphans,
            "no_missing_dependencies": self.check_missing_dependencies,
            "all_nodes_used": self.check_all_nodes_used,
            "no_undefined_references": self.check_no_undefined_references,
        }
        
        # Run selected policies
        policies_to_run = policies if policies else list(all_policies.keys())
        
        for policy_name in policies_to_run:
            if policy_name in all_policies:
                all_policies[policy_name]()
        
        return self.violations
    
    def check_no_cycles(self) -> None:
        """
        Policy: Graph must not contain cycles.
        
        Cycles indicate circular dependencies which can cause infinite loops.
        """
        cycles = self.graph.find_cycles()
        if cycles:
            for cycle in cycles:
                cycle_str = " -> ".join(cycle)
                self.violations.append(PolicyViolation(
                    rule_name="no_cycles",
                    severity=PolicySeverity.ERROR,
                    message=f"Circular dependency detected: {cycle_str}",
                    node_name=cycle[0] if cycle else None,
                    metadata={"cycle": cycle}
                ))
    
    def check_no_orphans(self) -> None:
        """
        Policy: No orphan nodes (nodes with no dependencies or dependents).
        
        Orphan nodes may indicate unused code or missing connections.
        """
        orphans = self.graph.find_orphans()
        if orphans:
            for orphan in orphans:
                node = self.graph.nodes.get(orphan)
                self.violations.append(PolicyViolation(
                    rule_name="no_orphans",
                    severity=PolicySeverity.WARNING,
                    message=f"Orphan node '{orphan}' has no dependencies or dependents",
                    node_name=orphan,
                    metadata={
                        "file_path": node.file_path if node else None,
                        "line_number": node.line_number if node else None
                    }
                ))
    
    def check_missing_dependencies(self) -> None:
        """
        Policy: All referenced dependencies must exist as nodes.
        
        Detects edges that reference nodes that don't exist in the graph.
        This can happen if a variable is referenced but never defined.
        """
        node_names = set(self.graph.nodes.keys())
        
        for edge in self.graph.edges:
            if edge.from_node not in node_names:
                self.violations.append(PolicyViolation(
                    rule_name="no_missing_dependencies",
                    severity=PolicySeverity.ERROR,
                    message=f"Edge references missing node '{edge.from_node}'",
                    node_name=edge.to_node,
                    edge_info={
                        "from": edge.from_node,
                        "to": edge.to_node,
                        "type": edge.dep_type.value
                    },
                    metadata={
                        "file_path": edge.file_path,
                        "line_number": edge.line_number
                    }
                ))
            
            if edge.to_node not in node_names:
                self.violations.append(PolicyViolation(
                    rule_name="no_missing_dependencies",
                    severity=PolicySeverity.ERROR,
                    message=f"Edge references missing node '{edge.to_node}'",
                    node_name=edge.from_node,
                    edge_info={
                        "from": edge.from_node,
                        "to": edge.to_node,
                        "type": edge.dep_type.value
                    },
                    metadata={
                        "file_path": edge.file_path,
                        "line_number": edge.line_number
                    }
                ))
    
    def check_all_nodes_used(self) -> None:
        """
        Policy: All nodes should be used (have at least one dependent or dependency).
        
        Nodes that are never referenced may indicate dead code.
        """
        used_nodes: Set[str] = set()
        
        # Collect all nodes that are referenced in edges
        for edge in self.graph.edges:
            used_nodes.add(edge.from_node)
            used_nodes.add(edge.to_node)
        
        # Check for unused nodes
        all_nodes = set(self.graph.nodes.keys())
        unused = all_nodes - used_nodes
        
        # Filter out roots (entry points are allowed to have no dependencies)
        roots = set(self.graph.find_roots())
        unused = unused - roots
        
        if unused:
            for node_name in unused:
                node = self.graph.nodes.get(node_name)
                self.violations.append(PolicyViolation(
                    rule_name="all_nodes_used",
                    severity=PolicySeverity.WARNING,
                    message=f"Node '{node_name}' is defined but never referenced",
                    node_name=node_name,
                    metadata={
                        "file_path": node.file_path if node else None,
                        "line_number": node.line_number if node else None,
                        "kind": node.kind.value if node else None
                    }
                ))
    
    def check_no_undefined_references(self) -> None:
        """
        Policy: Variables referenced in expressions must be defined.
        
        This is a stricter check that looks for implicit dependencies
        where the source variable might not exist.
        """
        # This is similar to check_missing_dependencies but focuses on
        # implicit dependencies which are more likely to be errors
        node_names = set(self.graph.nodes.keys())
        
        for edge in self.graph.edges:
            if edge.dep_type.value == "implicit" and edge.from_node not in node_names:
                node = self.graph.nodes.get(edge.to_node)
                self.violations.append(PolicyViolation(
                    rule_name="no_undefined_references",
                    severity=PolicySeverity.ERROR,
                    message=f"Implicit reference to undefined variable '{edge.from_node}' in '{edge.to_node}'",
                    node_name=edge.to_node,
                    edge_info={
                        "from": edge.from_node,
                        "to": edge.to_node,
                        "type": "implicit"
                    },
                    metadata={
                        "file_path": edge.file_path or (node.file_path if node else None),
                        "line_number": edge.line_number or (node.line_number if node else None)
                    }
                ))
    
    def get_summary(self) -> Dict[str, int]:
        """
        Get summary of validation results.
        
        Returns:
            Dictionary with counts by severity: total, errors, warnings, info
        """
        summary: Dict[str, int] = {
            "total": len(self.violations),
            "errors": len([v for v in self.violations if v.severity == PolicySeverity.ERROR]),
            "warnings": len([v for v in self.violations if v.severity == PolicySeverity.WARNING]),
            "info": len([v for v in self.violations if v.severity == PolicySeverity.INFO]),
        }
        return summary
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert validation results to dictionary for JSON serialization.
        
        Returns:
            Dictionary with summary and violations list
        """
        return {
            "summary": self.get_summary(),
            "violations": [v.to_dict() for v in self.violations]
        }
