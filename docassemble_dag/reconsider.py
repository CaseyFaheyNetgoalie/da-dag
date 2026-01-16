"""
Reconsider directive tracking for Docassemble interviews.

Docassemble's `reconsider:` directive forces re-evaluation of variables,
breaking static dependency assumptions. This module tracks these directives
and warns when dependencies cross reconsider boundaries.
"""

import logging
from typing import Dict, List, Optional, Set

from .graph import DependencyGraph

logger = logging.getLogger(__name__)


class ReconsiderDirective:
    """
    Represents a reconsider directive in a Docassemble interview.
    
    `reconsider:` forces re-evaluation of variables, which can break
    static dependency assumptions.
    """
    
    def __init__(
        self,
        node_name: str,
        reconsidered_var: str,
        line_number: Optional[int] = None,
        file_path: Optional[str] = None,
    ) -> None:
        """
        Initialize reconsider directive.
        
        Args:
            node_name: Name of the node containing the reconsider directive
            reconsidered_var: Name of the variable being reconsidered
            line_number: Optional line number
            file_path: Optional file path
        """
        self.node_name = node_name
        self.reconsidered_var = reconsidered_var
        self.line_number = line_number
        self.file_path = file_path


def extract_reconsider_directives(yaml_dict: Dict) -> List[ReconsiderDirective]:
    """
    Extract reconsider directives from parsed YAML.
    
    Args:
        yaml_dict: Parsed YAML dictionary
        
    Returns:
        List of ReconsiderDirective objects
    """
    directives: List[ReconsiderDirective] = []
    
    # Check all item types for reconsider directives
    for item_type in ['questions', 'rules', 'variables', 'fields']:
        items = yaml_dict.get(item_type, [])
        if not isinstance(items, list):
            items = []
        
        for item in items:
            if not isinstance(item, dict):
                continue
            
            node_name = item.get('name') or item.get('variable')
            if not node_name:
                continue
            
            # Check for reconsider directive
            reconsider_val = item.get('reconsider') or item.get('reconsider:')
            if reconsider_val:
                # reconsider can be a single variable or a list
                reconsidered_vars = reconsider_val if isinstance(reconsider_val, list) else [reconsider_val]
                
                for var in reconsidered_vars:
                    if isinstance(var, str):
                        directives.append(ReconsiderDirective(
                            node_name=node_name,
                            reconsidered_var=var,
                            file_path=None,  # Would need parser context
                        ))
    
    return directives


def check_reconsider_boundaries(
    graph: DependencyGraph,
    reconsider_directives: List[ReconsiderDirective],
) -> List[Dict]:
    """
    Check if dependencies cross reconsider boundaries.
    
    Warns when dependencies cross reconsider boundaries, as this can
    break static dependency assumptions.
    
    Args:
        graph: Dependency graph to check
        reconsider_directives: List of reconsider directives
        
    Returns:
        List of warning dictionaries
    """
    warnings: List[Dict] = []
    
    # Build map of reconsidered variables
    reconsidered_vars: Set[str] = {d.reconsidered_var for d in reconsider_directives}
    
    # Check each edge for crossing reconsider boundaries
    for edge in graph.edges:
        from_var = edge.from_node
        to_var = edge.to_node
        
        # If from_var is reconsidered, warn about dependency crossing
        if from_var in reconsidered_vars:
            warnings.append({
                "type": "reconsider_boundary",
                "message": f"Dependency from '{from_var}' to '{to_var}' crosses reconsider boundary",
                "from_node": from_var,
                "to_node": to_var,
                "warning": "Variable is reconsidered, which may break static dependency assumptions",
            })
    
    return warnings


def get_reconsidered_variables(reconsider_directives: List[ReconsiderDirective]) -> Set[str]:
    """
    Get set of all variables that are reconsidered.
    
    Args:
        reconsider_directives: List of reconsider directives
        
    Returns:
        Set of variable names that are reconsidered
    """
    return {d.reconsidered_var for d in reconsider_directives}
