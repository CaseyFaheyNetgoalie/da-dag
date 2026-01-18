"""
AST-based Python code analysis for better variable reference detection.

Uses Python's Abstract Syntax Tree to accurately parse Python code blocks
in Docassemble interviews, providing more accurate dependency detection than
regex-based approaches.
"""

import ast
import logging
from typing import Set, Tuple

from .exceptions import ParsingError

logger = logging.getLogger(__name__)

# Resource limits for AST parsing
MAX_AST_NODES = 10000  # Maximum number of AST nodes to process
MAX_AST_DEPTH = 100  # Maximum AST depth
MAX_CODE_SIZE = 100000  # Maximum code size in characters (100KB)


class VariableVisitor(ast.NodeVisitor):
    """
    AST visitor that extracts variable references from Python code.
    
    Tracks variable names that are loaded (read) from, which represent
    dependencies in Docassemble interviews.
    """
    
    def __init__(self) -> None:
        """Initialize visitor with empty variable sets."""
        self.variables: Set[str] = set()  # Variables that are read (dependencies)
        self.objects: Set[str] = set()  # Objects used for attribute access
        self.attributes: Set[tuple] = set()  # (object, attribute) pairs
    
    def visit_Name(self, node: ast.Name) -> None:
        """
        Visit a Name node (variable reference).
        
        Track variables that are loaded (read from), which indicate dependencies.
        Ignore variables that are stored (assigned to) as they're definitions.
        
        Args:
            node: AST Name node representing a variable reference
        """
        if isinstance(node.ctx, ast.Load):
            # Variable is being read (dependency)
            self.variables.add(node.id)
        # Ignore Store and Del contexts (these are assignments, not dependencies)
    
    def visit_Attribute(self, node: ast.Attribute) -> None:
        """
        Visit an Attribute node (object.attribute access).
        
        Track object names used for attribute access, e.g., person.name
        creates a dependency on 'person', not 'name'.
        
        Args:
            node: AST Attribute node representing object.attribute access
        """
        # Recursively visit the value (object) part
        self.visit(node.value)
        
        # If the value is a Name, track the object
        if isinstance(node.value, ast.Name):
            obj_name = node.value.id
            attr_name = node.attr
            self.objects.add(obj_name)
            self.attributes.add((obj_name, attr_name))
    
    def visit_Subscript(self, node: ast.Subscript) -> None:
        """
        Visit a Subscript node (e.g., obj[key]).
        
        Track the object being subscripted.
        
        Args:
            node: AST Subscript node
        """
        self.visit(node.value)
        self.visit(node.slice)
    
    def visit_Call(self, node: ast.Call) -> None:
        """
        Visit a Call node (function call).
        
        Track function name and arguments, but don't treat function calls
        as dependencies unless they're variables being called.
        
        Args:
            node: AST Call node representing a function call
        """
        # Visit the function being called (might be a variable)
        self.visit(node.func)
        # Visit all arguments
        for arg in node.args:
            self.visit(arg)
        for keyword in node.keywords:
            self.visit(keyword.value)


def extract_variables_from_python_ast(code: str) -> Tuple[Set[str], Set[str], Set[Tuple[str, str]]]:
    """
    Parse Python code using AST to extract variable references.
    
    This is more accurate than regex-based parsing because it understands
    Python syntax and only extracts actual variable references, not keywords,
    builtins, or other non-variable identifiers.
    
    Args:
        code: Python code as string
        
    Returns:
        Tuple of:
        - Set of variable names that are read (dependencies)
        - Set of object names used for attribute access
        - Set of (object, attribute) tuples
        
    Example:
        >>> code = "result = person.name + age"
        >>> vars, objs, attrs = extract_variables_from_python_ast(code)
        >>> vars
        {'person', 'age'}
        >>> objs
        {'person'}
        >>> attrs
        {('person', 'name')}
    """
    if not isinstance(code, str) or not code.strip():
        return set(), set(), set()
    
    # Check resource limits
    if len(code) > MAX_CODE_SIZE:
        logger.warning(
            f"Python code block too large: {len(code)} chars (max {MAX_CODE_SIZE}). "
            "Skipping AST parsing."
        )
        return set(), set(), set()
    
    try:
        tree = ast.parse(code, mode='exec')
    except SyntaxError as e:
        logger.debug(f"Failed to parse Python code as AST: {e}. Falling back to regex.")
        return set(), set(), set()
    except RecursionError:
        logger.warning("Recursion error parsing AST - code too complex or nested")
        return set(), set(), set()
    except Exception as e:
        logger.warning(f"Unexpected error parsing Python AST: {e}")
        return set(), set(), set()
    
    # Count AST nodes to prevent resource exhaustion
    node_count = len(list(ast.walk(tree)))
    if node_count > MAX_AST_NODES:
        logger.warning(
            f"AST too large: {node_count} nodes (max {MAX_AST_NODES}). "
            "Skipping AST parsing."
        )
        return set(), set(), set()
    
    # Check AST depth
    def get_ast_depth(node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum depth of AST."""
        if current_depth > MAX_AST_DEPTH:
            raise ParsingError(
                f"AST depth exceeds maximum {MAX_AST_DEPTH}. "
                "Code is too deeply nested."
            )
        
        max_depth = current_depth
        for child in ast.iter_child_nodes(node):
            max_depth = max(max_depth, get_ast_depth(child, current_depth + 1))
        return max_depth
    
    try:
        ast_depth = get_ast_depth(tree)
        if ast_depth > MAX_AST_DEPTH:
            logger.warning(f"AST depth {ast_depth} exceeds maximum {MAX_AST_DEPTH}")
            return set(), set(), set()
    except ParsingError:
        return set(), set(), set()
    
    visitor = VariableVisitor()
    visitor.visit(tree)
    
    return visitor.variables, visitor.objects, visitor.attributes


def should_use_ast_parsing(text: str) -> bool:
    """
    Determine if text should be parsed with AST (Python code) vs regex (expressions).
    
    Heuristic: If text contains multiple lines, statements, or Python keywords,
    it's likely Python code that would benefit from AST parsing.
    
    Args:
        text: Text to analyze
        
    Returns:
        True if AST parsing is recommended, False for regex
    """
    if not isinstance(text, str) or not text.strip():
        return False
    
    # Python keywords that suggest actual code
    python_keywords = {
        'def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 'except',
        'finally', 'with', 'import', 'from', 'return', 'yield', 'raise', 'assert',
        'break', 'continue', 'pass', 'lambda', 'async', 'await'
    }
    
    # If text contains Python keywords, use AST
    words = text.split()
    if any(word in python_keywords for word in words):
        return True
    
    # If text contains multiple statements (multiple lines)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if len(lines) > 2:
        # Multiple lines suggests code block
        return True
    if len(lines) > 1:
        # Two lines: check if any has assignment or statement
        if any('=' in line or ':' in line for line in lines):
            return True
    
    # If text looks like a simple expression (single line, no colons), use regex
    return False
