"""
Core data types for representing the dependency graph.

These types are framework-agnostic and represent the core domain model.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any


class NodeKind(Enum):
    """Type of node in the dependency graph."""
    VARIABLE = "variable"
    QUESTION = "question"
    RULE = "rule"
    ASSEMBLY_LINE = "assembly_line"  # Assembly Line variable (AL_ prefix)


class DependencyType(Enum):
    """Type of dependency relationship."""
    EXPLICIT = "explicit"  # e.g., `depends on:` or `required:`
    IMPLICIT = "implicit"  # variable referenced in expression, template, etc.


@dataclass
class Node:
    """
    A node in the dependency graph.
    
    Represents a variable, question, or rule in the Docassemble interview.
    
    Enhanced with provenance metadata similar to GUAC's artifact tracking.
    """
    name: str
    kind: NodeKind
    source: str  # "user_input" or "derived"
    authority: Optional[str] = None  # e.g., statute citation or rule name
    file_path: Optional[str] = None  # Source file path (for provenance)
    line_number: Optional[int] = None  # Line number in source file
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata


@dataclass
class Edge:
    """
    A directed edge in the dependency graph.
    
    Represents that `to_node` depends on `from_node`.
    
    Enhanced with provenance metadata for tracking where dependencies are defined.
    """
    from_node: str  # name of dependency (source)
    to_node: str  # node that depends (target)
    dep_type: DependencyType
    file_path: Optional[str] = None  # Source file path where edge is defined
    line_number: Optional[int] = None  # Line number where dependency is expressed
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata