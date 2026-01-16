"""
Conditional logic detection for Docassemble interviews.

Extracts conditional dependencies from `show if:`, `enable if:`, `required if:`,
and other conditional directives that create implicit dependencies.
"""

import logging
import re
from typing import Dict, List, Optional, Set

from .ast_parser import extract_variables_from_python_ast, should_use_ast_parsing
from .types import DependencyType

logger = logging.getLogger(__name__)

# Pattern to match conditional directives
CONDITIONAL_PATTERN = re.compile(
    r'\b(show\s+if|enable\s+if|required\s+if|hide\s+if|disable\s+if|mandatory\s+if)\s*[:=]\s*(.+?)(?=\n|$)',
    re.IGNORECASE | re.MULTILINE
)


class ConditionalDependency:
    """
    Represents a conditional dependency from a conditional directive.
    
    For example, `show if: age >= 18` creates a dependency on `age`.
    """
    
    def __init__(
        self,
        directive: str,
        condition: str,
        dependent_node: str,
        line_number: Optional[int] = None,
    ) -> None:
        """
        Initialize conditional dependency.
        
        Args:
            directive: The conditional directive (e.g., "show if", "enable if")
            condition: The conditional expression (e.g., "age >= 18")
            dependent_node: The node that depends on the condition
            line_number: Line number where directive is found
        """
        self.directive = directive.lower().strip()
        self.condition = condition.strip()
        self.dependent_node = dependent_node
        self.line_number = line_number
        self.dependencies: Set[str] = set()
        self._extract_dependencies()
    
    def _extract_dependencies(self) -> None:
        """Extract variable dependencies from the conditional expression."""
        # Use AST parsing for complex conditions, regex for simple ones
        if should_use_ast_parsing(self.condition):
            try:
                variables, objects, _ = extract_variables_from_python_ast(self.condition)
                self.dependencies.update(variables)
                self.dependencies.update(objects)
            except Exception as e:
                logger.debug(f"AST parsing failed for condition '{self.condition}': {e}. Using regex.")
                self._extract_with_regex()
        else:
            self._extract_with_regex()
    
    def _extract_with_regex(self) -> None:
        """Extract variable dependencies using regex as fallback."""
        # Simple variable name pattern
        var_pattern = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b')
        
        # Python keywords and operators to exclude
        excluded = {
            'and', 'or', 'not', 'in', 'is', 'if', 'else', 'elif',
            'True', 'False', 'None', 'len', 'str', 'int', 'float',
            'bool', 'list', 'dict', 'set', 'tuple',
        }
        
        matches = var_pattern.findall(self.condition)
        for match in matches:
            if match.lower() not in excluded and not match[0].isupper():
                # Skip Python built-ins and keywords
                self.dependencies.add(match)


def extract_conditional_dependencies(
    yaml_content: str,
    node_name: str,
    line_number: Optional[int] = None,
) -> List[ConditionalDependency]:
    """
    Extract conditional dependencies from YAML content.
    
    Looks for conditional directives like `show if:`, `enable if:`, etc.
    and extracts the variables they depend on.
    
    Args:
        yaml_content: YAML content (may be a section or full file)
        node_name: Name of the node that has the conditional logic
        line_number: Optional line number for provenance
        
    Returns:
        List of ConditionalDependency objects
        
    Example:
        >>> yaml = 'question: "What is your age?"\\nshow if: age >= 18'
        >>> deps = extract_conditional_dependencies(yaml, "ask_age", line_num=42)
        >>> deps[0].dependencies
        {'age'}
    """
    dependencies: List[ConditionalDependency] = []
    
    # Look for conditional directives in the YAML content
    # These can appear at the top level or within question/field definitions
    for match in CONDITIONAL_PATTERN.finditer(yaml_content):
        directive = match.group(1).strip()
        condition = match.group(2).strip()
        
        # Create conditional dependency
        cond_dep = ConditionalDependency(
            directive=directive,
            condition=condition,
            dependent_node=node_name,
            line_number=line_number,
        )
        
        if cond_dep.dependencies:
            dependencies.append(cond_dep)
    
    # Also check for conditional directives in YAML structure (parsed)
    # This is handled by the parser when it processes items
    
    return dependencies


def extract_conditionals_from_item(
    item: Dict,
    node_name: str,
    line_number: Optional[int] = None,
) -> List[ConditionalDependency]:
    """
    Extract conditional dependencies from a parsed YAML item.
    
    Checks for conditional keys in the item dictionary.
    
    Args:
        item: Parsed YAML item (dict)
        node_name: Name of the node
        line_number: Optional line number
        
    Returns:
        List of ConditionalDependency objects
    """
    dependencies: List[ConditionalDependency] = []
    
    # Common conditional directive keys in Docassemble
    conditional_keys = [
        'show if',
        'show_if',
        'enable if',
        'enable_if',
        'required if',
        'required_if',
        'hide if',
        'hide_if',
        'disable if',
        'disable_if',
        'mandatory if',
        'mandatory_if',
    ]
    
    # Check for conditional keys (prefer space-separated, then underscore)
    seen_conditions: Set[str] = set()
    for key in conditional_keys:
        # Try space-separated first (preferred in YAML)
        condition = item.get(key.replace('_', ' '))
        if not condition:
            # Fall back to underscore
            condition = item.get(key)
        
        if condition and isinstance(condition, str):
            # Avoid duplicates if both 'show if' and 'show_if' exist
            if condition not in seen_conditions:
                seen_conditions.add(condition)
                cond_dep = ConditionalDependency(
                    directive=key.replace('_', ' '),  # Normalize to space
                    condition=condition,
                    dependent_node=node_name,
                    line_number=line_number,
                )
                if cond_dep.dependencies:
                    dependencies.append(cond_dep)
    
    return dependencies


def get_conditional_edges(
    conditional_deps: List[ConditionalDependency],
    nodes: Dict,
) -> List[tuple]:
    """
    Convert conditional dependencies to edge tuples.
    
    Args:
        conditional_deps: List of conditional dependencies
        nodes: Dictionary of nodes to validate against
        
    Returns:
        List of (from_node, to_node, dep_type, directive, line_number) tuples
    """
    edges: List[tuple] = []
    
    for cond_dep in conditional_deps:
        for dep_var in cond_dep.dependencies:
            if dep_var in nodes:
                edges.append((
                    dep_var,
                    cond_dep.dependent_node,
                    DependencyType.IMPLICIT,
                    cond_dep.directive,
                    cond_dep.line_number,
                ))
    
    return edges
