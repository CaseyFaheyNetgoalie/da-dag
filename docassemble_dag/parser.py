"""
Parser for Docassemble YAML interview files.

Extracts variables, questions, rules, and their dependencies from YAML.
"""

import logging
import re
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import yaml

from .ast_parser import extract_variables_from_python_ast, should_use_ast_parsing
from .conditional import extract_conditionals_from_item
from .exceptions import InvalidYAMLError, ParsingError
from .schema import validate_yaml_structure
from .types import DependencyType, Edge, Node, NodeKind

logger = logging.getLogger(__name__)


# Pattern to match variable references in expressions/templates
# Simple heuristic: matches identifiers that look like variable names
VARIABLE_REF_PATTERN = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b')

# Pattern to match object attribute access (person.name, address.street)
# Captures both the object and attribute
OBJECT_ATTR_PATTERN = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\b')

# Pattern to detect Assembly Line variables (AL_ prefix)
ASSEMBLY_LINE_PREFIX = 'AL_'


class DocassembleParser:
    """
    Parser for Docassemble YAML interview files.
    
    Performs static analysis only - does not execute or validate the interview.
    Enhanced with provenance tracking (file paths, line numbers).
    """
    
    def __init__(self, yaml_text: str, file_path: Optional[str] = None) -> None:
        """
        Initialize parser with YAML content.
        
        Args:
            yaml_text: Raw YAML content as string
            file_path: Optional file path for provenance tracking
            
        Raises:
            ValueError: If YAML does not parse to a dictionary structure
            yaml.YAMLError: If YAML parsing fails
        """
        if not isinstance(yaml_text, str):
            raise TypeError(
                f"yaml_text must be a string, got {type(yaml_text).__name__}"
            )
        
        self.file_path = file_path
        self.yaml_text = yaml_text
        self.yaml_lines = yaml_text.split('\n') if yaml_text else []
        
        try:
            self.raw = yaml.safe_load(yaml_text)
        except yaml.YAMLError as e:
            raise InvalidYAMLError(
                f"Failed to parse YAML: {e}. Please ensure the file contains valid YAML syntax.",
                file_path=file_path,
                original_error=e,
            ) from e
        
        if self.raw is None:
            self.raw = {}
        
        if not isinstance(self.raw, dict):
            raise InvalidYAMLError(
                f"YAML must parse to a dictionary structure, got {type(self.raw).__name__}. "
                "Please ensure the root element is a YAML object (key-value pairs).",
                file_path=file_path,
            )
        
        # Validate YAML structure
        validation_errors = validate_yaml_structure(self.raw)
        if validation_errors:
            raise InvalidYAMLError(
                f"YAML structure validation failed: {'; '.join(validation_errors)}",
                file_path=file_path,
            )
        
        logger.debug(
            f"Initialized parser for {file_path or 'string input'} "
            f"({len(self.yaml_lines)} lines)"
        )
    
    def _find_line_number(self, key: str, item: Dict[str, Any]) -> Optional[int]:
        """
        Find approximate line number for a YAML key in the source text.
        
        This is a heuristic - finds the first occurrence of the key.
        For more accurate line numbers, would need to use ruamel.yaml with line info.
        
        Args:
            key: The YAML key to find
            item: Dictionary item containing the key
            
        Returns:
            Line number (1-based) or None if not found
        """
        if not self.yaml_lines:
            return None
        
        name = self._get_name(item)
        if not name:
            return None
        
        # Search for the key name in the YAML
        for i, line in enumerate(self.yaml_lines, 1):
            if name in line and (
                f'name: {name}' in line 
                or f'"{name}"' in line 
                or f"'{name}'" in line
            ):
                return i
        
        return None
    
    def _find_line_number_by_name(self, name: str) -> Optional[int]:
        """
        Find approximate line number for a node name in the YAML text.
        
        Args:
            name: The node name to find
            
        Returns:
            Line number (1-based) or None if not found
        """
        if not self.yaml_lines or not name:
            return None
        
        for i, line in enumerate(self.yaml_lines, 1):
            if name in line and (
                f'name: {name}' in line 
                or f'"{name}"' in line 
                or f"'{name}'" in line
            ):
                return i
        
        return None
    
    def _extract_implicit_dependencies(
        self,
        text: str,
        dst_name: str,
        line_num: Optional[int],
        add_edge: Callable[[str, str, DependencyType, Optional[int]], None],
    ) -> None:
        """
        Extract implicit dependencies from text containing variable references.
        
        Uses AST parsing for Python code blocks for better accuracy,
        falls back to regex for simple expressions and templates.
        
        Handles both object attributes (person.name → person) and regular
        variable references, avoiding double-matching.
        
        Args:
            text: Text to analyze (expression, template, code, etc.)
            dst_name: Name of the node that depends on variables in text
            line_num: Line number where text is located
            add_edge: Function to call to add edges (from_node, to_node, dep_type, line_num)
        """
        if not isinstance(text, str) or not text.strip():
            return
        
        # Try AST parsing for Python code blocks (more accurate)
        if should_use_ast_parsing(text):
            try:
                variables, objects, attributes = extract_variables_from_python_ast(text)
                processed_objects: Set[str] = set()
                
                # Handle object attributes first (person.name → person dependency)
                for obj_name, _ in attributes:
                    if obj_name != dst_name and obj_name not in processed_objects:
                        add_edge(obj_name, dst_name, DependencyType.IMPLICIT, line_num)
                        processed_objects.add(obj_name)
                
                # Handle regular variable references (avoid double-matching)
                for var_name in variables:
                    if (
                        var_name != dst_name
                        and var_name not in processed_objects
                        and var_name not in objects  # Objects already handled above
                    ):
                        add_edge(var_name, dst_name, DependencyType.IMPLICIT, line_num)
                
                # AST parsing succeeded, return early
                return
            except Exception as e:
                logger.debug(f"AST parsing failed for code block, falling back to regex: {e}")
                # Fall through to regex-based parsing
        
        # Fallback to regex-based parsing for expressions and templates
        # First, handle object attributes (person.name → person dependency)
        object_attrs = OBJECT_ATTR_PATTERN.findall(text)
        processed_objects: Set[str] = set()
        
        for obj_name, _ in object_attrs:
            if obj_name != dst_name and obj_name not in processed_objects:
                add_edge(obj_name, dst_name, DependencyType.IMPLICIT, line_num)
                processed_objects.add(obj_name)
        
        # Then handle regular variable references (avoid double-matching)
        for match in VARIABLE_REF_PATTERN.findall(text):
            ref_name = match
            # Skip if it's the node's own name (self-reference)
            # Skip if it's an object we already processed (person.name already handled as person)
            if (
                ref_name != dst_name
                and ref_name not in processed_objects
                and not any(ref_name == obj_name for obj_name, _ in object_attrs)
            ):
                add_edge(ref_name, dst_name, DependencyType.IMPLICIT, line_num)
    
    def extract_nodes(self) -> Dict[str, Node]:
        """
        Extract all nodes (variables, questions, rules) from the YAML.
        
        Returns:
            Dictionary mapping node name to Node object
        """
        nodes: Dict[str, Node] = {}
        
        # Extract variables (fields)
        # Docassemble uses various keys: 'fields', 'variables', or items with 'variable' key
        # Merge both 'fields' and 'variables' if both exist
        variables = []
        for key in ['fields', 'variables']:
            items = self.raw.get(key, [])
            if isinstance(items, list):
                variables.extend(items)
        
        for var in variables:
            name = self._get_name(var)
            if not name:
                continue
            
            # Check if variable has an expression (derived) or is user input
            has_expression = bool(var.get('expression') or var.get('code'))
            source = "derived" if has_expression else "user_input"
            
            # Detect Assembly Line variables (AL_ prefix)
            kind = NodeKind.ASSEMBLY_LINE if name.startswith(ASSEMBLY_LINE_PREFIX) else NodeKind.VARIABLE
            
            # Find line number by searching YAML text
            line_num = self._find_line_number_by_name(name)
            
            nodes[name] = Node(
                name=name,
                kind=kind,
                source=source,
                authority=var.get('authority') or var.get('statute'),
                file_path=self.file_path,
                line_number=line_num
            )
        
        # Extract questions
        # Questions can be under 'questions' key or as top-level items with 'question' key
        questions = self.raw.get('questions', [])
        if not isinstance(questions, list):
            questions = []
        
        for q in questions:
            name = self._get_name(q)
            if not name:
                continue
            
            nodes[name] = Node(
                name=name,
                kind=NodeKind.QUESTION,
                source="user_input",  # Questions typically collect user input
                authority=q.get('authority') or q.get('statute'),
                file_path=self.file_path,
                line_number=self._find_line_number('name', q)
            )
            
            # Questions may implicitly define variables via 'variable' key
            var_name = q.get('variable') or q.get('field')
            if var_name and var_name not in nodes:
                nodes[var_name] = Node(
                    name=var_name,
                    kind=NodeKind.VARIABLE,
                    source="user_input",
                    authority=None,
                    file_path=self.file_path,
                    line_number=self._find_line_number('variable', q)
                )
        
        # Extract rules
        rules = self.raw.get('rules', [])
        if not isinstance(rules, list):
            rules = []
        
        for rule in rules:
            name = self._get_name(rule)
            if not name:
                continue
            
            nodes[name] = Node(
                name=name,
                kind=NodeKind.RULE,
                source="derived",  # Rules are typically derived/computed
                authority=rule.get('authority') or rule.get('statute'),
                file_path=self.file_path,
                line_number=self._find_line_number('name', rule)
            )
        
        # Handle top-level items that might be questions or variables
        # (Some Docassemble formats use top-level items)
        for key, value in self.raw.items():
            if key in ('questions', 'variables', 'fields', 'rules'):
                continue
            
            if isinstance(value, dict):
                # If it has a 'question' key, treat as question
                if 'question' in value:
                    name = self._get_name(value) or key
                    if name not in nodes:
                        nodes[name] = Node(
                            name=name,
                            kind=NodeKind.QUESTION,
                            source="user_input",
                            authority=value.get('authority') or value.get('statute'),
                            file_path=self.file_path,
                            line_number=self._find_line_number('name', value)
                        )
                    
                    # Check for associated variable
                    var_name = value.get('variable') or value.get('field')
                    if var_name and var_name not in nodes:
                        nodes[var_name] = Node(
                            name=var_name,
                            kind=NodeKind.VARIABLE,
                            source="user_input",
                            authority=None,
                            file_path=self.file_path,
                            line_number=self._find_line_number('variable', value)
                        )
                
                # If it has 'expression' or 'code', treat as variable/rule
                elif 'expression' in value or 'code' in value:
                    name = self._get_name(value) or key
                    if name not in nodes:
                        nodes[name] = Node(
                            name=name,
                            kind=NodeKind.VARIABLE,  # Default to variable
                            source="derived",
                            authority=value.get('authority') or value.get('statute'),
                            file_path=self.file_path,
                            line_number=self._find_line_number('name', value)
                        )
        
        return nodes
    
    def extract_edges(self, nodes: Dict[str, Node]) -> List[Edge]:
        """
        Extract dependency edges (explicit and implicit) from the YAML.
        
        Args:
            nodes: Dictionary of nodes to validate dependencies against
        
        Returns:
            List of Edge objects representing dependencies
        """
        edges: List[Edge] = []
        edges_seen: Set[tuple] = set()  # Track (from, to) pairs to avoid duplicates
        
        # Helper to add edge if not duplicate
        def add_edge(from_node: str, to_node: str, dep_type: DependencyType, line_num: Optional[int] = None):
            if from_node in nodes and to_node in nodes:
                edge_key = (from_node, to_node)
                if edge_key not in edges_seen and from_node != to_node:
                    edges.append(Edge(
                        from_node=from_node,
                        to_node=to_node,
                        dep_type=dep_type,
                        file_path=self.file_path,
                        line_number=line_num
                    ))
                    edges_seen.add(edge_key)
        
        # Extract explicit dependencies
        for item_type in ['questions', 'rules', 'variables', 'fields']:
            items = self.raw.get(item_type, [])
            if not isinstance(items, list):
                items = []
            
            for item in items:
                dst_name = self._get_name(item)
                if not dst_name:
                    continue
                
                # Check for explicit dependency keys
                for dep_key in ['depends on', 'depends_on', 'required', 'requires', 'mandatory']:
                    deps = item.get(dep_key)
                    if deps:
                        deps_list = deps if isinstance(deps, list) else [deps]
                        line_num = self._find_line_number(dep_key, item)
                        for dep in deps_list:
                            if isinstance(dep, str):
                                add_edge(dep, dst_name, DependencyType.EXPLICIT, line_num)
                
                # Extract conditional dependencies (show if, enable if, etc.)
                line_num = self._find_line_number('name', item)
                conditional_deps = extract_conditionals_from_item(item, dst_name, line_num)
                for cond_dep in conditional_deps:
                    for dep_var in cond_dep.dependencies:
                        if dep_var in nodes:
                            add_edge(dep_var, dst_name, DependencyType.IMPLICIT, line_num)
        
        # Extract implicit dependencies via variable references
        # Scan expressions, templates, question text, choices, etc.
        for item_type in ['questions', 'rules', 'variables', 'fields']:
            items = self.raw.get(item_type, [])
            if not isinstance(items, list):
                items = []
            
            for item in items:
                dst_name = self._get_name(item)
                if not dst_name:
                    continue
                
                # Fields that may contain variable references
                text_fields = ['expression', 'template', 'question', 'choices', 'default', 'code']
                for field_name in text_fields:
                    text = item.get(field_name)
                    if isinstance(text, str):
                        line_num = self._find_line_number(field_name, item)
                        self._extract_implicit_dependencies(
                            text, dst_name, line_num, add_edge
                        )
        
        # Also check top-level items
        for key, value in self.raw.items():
            if key in ('questions', 'variables', 'fields', 'rules'):
                continue
            
            if isinstance(value, dict):
                dst_name = self._get_name(value) or key
                
                # Check explicit dependencies
                for dep_key in ['depends on', 'depends_on', 'required', 'requires', 'mandatory']:
                    deps = value.get(dep_key)
                    if deps:
                        deps_list = deps if isinstance(deps, list) else [deps]
                        line_num = self._find_line_number(dep_key, value)
                        for dep in deps_list:
                            if isinstance(dep, str):
                                add_edge(dep, dst_name, DependencyType.EXPLICIT, line_num)
                
                # Check implicit dependencies
                text_fields = ['expression', 'template', 'question', 'choices', 'default', 'code']
                for field_name in text_fields:
                    text = value.get(field_name)
                    if isinstance(text, str):
                        line_num = self._find_line_number(field_name, value)
                        self._extract_implicit_dependencies(
                            text, dst_name, line_num, add_edge
                        )
        
        return edges
    
    def get_modules(self) -> List[str]:
        """
        Extract modules: directive from YAML.
        
        Returns list of module names (e.g., 'docassemble.income', 'docassemble.base.legal').
        These represent cross-repository dependencies.
        
        Returns:
            List of module names
        """
        modules = []
        
        # Check top-level 'modules:' key
        modules_val = self.raw.get('modules', [])
        if isinstance(modules_val, list):
            modules.extend([str(m) for m in modules_val if isinstance(m, str)])
        elif isinstance(modules_val, str):
            modules.append(modules_val)
        
        # Also check 'modules' as a single module name
        if isinstance(self.raw.get('module'), str):
            modules.append(self.raw['module'])
        
        return modules
    
    def _get_name(self, item: Dict[str, Any]) -> Optional[str]:
        """
        Extract name from an item (variable, question, or rule).
        
        Handles various Docassemble naming conventions.
        
        Returns:
            Node name as string, or None if not found
        """
        if not isinstance(item, dict):
            return None
        
        # Try common name keys
        for key in ['name', 'id', 'variable', 'field']:
            if key in item:
                name = item[key]
                if isinstance(name, str):
                    return name
        
        return None
