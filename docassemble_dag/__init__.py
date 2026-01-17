"""
Docassemble DAG: Static analyzer for extracting explicit dependency graphs
from Docassemble YAML interview files.

Copyright 2024

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

__version__ = "0.5.0"

from .comparison import GraphDiff, compare_graphs, get_change_impact
from .compliance import ComplianceReport, generate_compliance_report
from .conditional import ConditionalDependency, extract_conditionals_from_item
from .decision_trees import DecisionNode, DecisionTree, decision_tree_to_dot, extract_decision_tree
from .exceptions import (
    CycleError,
    DocassembleDAGError,
    GraphError,
    InvalidYAMLError,
    ParsingError,
    StorageError,
    ValidationError,
)
from .graph import DependencyGraph
from .graph_operations import get_dependency_layers, get_execution_order, topological_sort
from .parser import DocassembleParser
from .persistence import GraphStorage, load_graph_json, save_graph_json
from .db_backends import DatabaseBackend, PostgreSQLBackend, SQLiteBackend, get_backend
from .reconsider import (
    ReconsiderDirective,
    check_reconsider_boundaries,
    extract_reconsider_directives,
    get_reconsidered_variables,
)
from .types import DependencyType, Edge, Node, NodeKind
from .utils import (
    find_nodes_by_authority,
    find_yaml_files,
    merge_graphs,
    parse_multiple_files,
    parse_with_includes,
)
from .validation import GraphValidator, PolicySeverity, PolicyViolation
from .graphql.schema import create_schema
from .graphql.server import create_server

__all__ = [
    # Core types
    "Node",
    "NodeKind",
    "Edge",
    "DependencyType",
    # Core classes
    "DocassembleParser",
    "DependencyGraph",
    # Exceptions
    "DocassembleDAGError",
    "InvalidYAMLError",
    "ParsingError",
    "GraphError",
    "CycleError",
    "ValidationError",
    "StorageError",
    # Graph operations
    "topological_sort",
    "get_execution_order",
    "get_dependency_layers",
    # Validation
    "GraphValidator",
    "PolicyViolation",
    "PolicySeverity",
    # Comparison
    "GraphDiff",
    "compare_graphs",
    "get_change_impact",
    # Conditional logic
    "ConditionalDependency",
    "extract_conditionals_from_item",
    # Decision trees
    "DecisionTree",
    "DecisionNode",
    "extract_decision_tree",
    "decision_tree_to_dot",
    # Persistence
    "GraphStorage",
    "save_graph_json",
    "load_graph_json",
    # Database backends
    "DatabaseBackend",
    "SQLiteBackend",
    "PostgreSQLBackend",
    "get_backend",
    # Compliance
    "ComplianceReport",
    "generate_compliance_report",
    # Reconsider
    "ReconsiderDirective",
    "extract_reconsider_directives",
    "check_reconsider_boundaries",
    "get_reconsidered_variables",
    # Utilities
    "find_yaml_files",
    "merge_graphs",
    "parse_multiple_files",
    "find_nodes_by_authority",
    "parse_with_includes",
    "create_schema", 
    "create_server"
]

# Assembly Line and object attribute support available in v0.3+
# NodeKind.ASSEMBLY_LINE - for variables with AL_ prefix
# Object attribute parsing (person.name → person dependency)
# Modules: directive parsing (get_modules())
