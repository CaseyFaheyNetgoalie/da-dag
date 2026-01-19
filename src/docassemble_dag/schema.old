"""
YAML schema types and validation.

Provides TypedDict definitions for Docassemble YAML structures
to improve type safety and validation.
"""

from typing import TypedDict, List, Optional, Dict, Any, Union


class YAMLQuestion(TypedDict, total=False):
    """Type definition for a Docassemble question item."""
    name: str
    question: str
    variable: str
    required: Union[str, List[str]]
    depends_on: Union[str, List[str]]
    show_if: str
    enable_if: str
    choices: List[str]
    authority: str
    file_path: str
    line_number: int


class YAMLVariable(TypedDict, total=False):
    """Type definition for a Docassemble variable item."""
    name: str
    expression: str
    code: str
    default: Any
    authority: str
    file_path: str
    line_number: int


class YAMLRule(TypedDict, total=False):
    """Type definition for a Docassemble rule item."""
    name: str
    expression: str
    code: str
    authority: str
    description: str
    file_path: str
    line_number: int


class YAMLField(TypedDict, total=False):
    """Type definition for a Docassemble field item."""
    name: str
    expression: str
    code: str
    default: Any
    authority: str
    file_path: str
    line_number: int


class YAMLInterview(TypedDict, total=False):
    """Type definition for a Docassemble interview YAML root."""
    questions: List[YAMLQuestion]
    variables: List[YAMLVariable]
    fields: List[YAMLField]
    rules: List[YAMLRule]
    include: Union[str, List[str]]
    modules: Union[str, List[str]]
    metadata: Dict[str, Any]


def is_valid_question(item: Dict[str, Any]) -> bool:
    """
    Validate if a dictionary represents a valid question item.
    
    Args:
        item: Dictionary to validate
        
    Returns:
        True if item is a valid question structure
    """
    if not isinstance(item, dict):
        return False
    
    # Question must have either 'name' or 'question' field
    if not ('name' in item or 'question' in item):
        return False
    
    return True


def is_valid_variable(item: Dict[str, Any]) -> bool:
    """
    Validate if a dictionary represents a valid variable item.
    
    Args:
        item: Dictionary to validate
        
    Returns:
        True if item is a valid variable structure
    """
    if not isinstance(item, dict):
        return False
    
    # Variable must have 'name' field
    if 'name' not in item:
        return False
    
    return True


def is_valid_rule(item: Dict[str, Any]) -> bool:
    """
    Validate if a dictionary represents a valid rule item.
    
    Args:
        item: Dictionary to validate
        
    Returns:
        True if item is a valid rule structure
    """
    if not isinstance(item, dict):
        return False
    
    # Rule must have 'name' field
    if 'name' not in item:
        return False
    
    return True


def is_valid_field(item: Dict[str, Any]) -> bool:
    """
    Validate if a dictionary represents a valid field item.
    
    Args:
        item: Dictionary to validate
        
    Returns:
        True if item is a valid field structure
    """
    if not isinstance(item, dict):
        return False
    
    # Field must have 'name' field
    if 'name' not in item:
        return False
    
    return True


def validate_yaml_structure(yaml_dict: Dict[str, Any]) -> List[str]:
    """
    Validate YAML structure against Docassemble interview schema.
    
    Args:
        yaml_dict: Parsed YAML dictionary
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors: List[str] = []
    
    if not isinstance(yaml_dict, dict):
        errors.append("YAML root must be a dictionary")
        return errors
    
    # Validate each section
    for section_name in ['questions', 'variables', 'fields', 'rules']:
        if section_name in yaml_dict:
            items = yaml_dict[section_name]
            if not isinstance(items, list):
                errors.append(f"{section_name} must be a list, got {type(items).__name__}")
                continue
            
            # Validate each item in the section
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    errors.append(f"{section_name}[{i}] must be a dictionary, got {type(item).__name__}")
                    continue
                
                # Section-specific validation
                if section_name == 'questions':
                    if not is_valid_question(item):
                        errors.append(f"{section_name}[{i}] is not a valid question (missing 'name' or 'question')")
                elif section_name in ('variables', 'fields'):
                    if not is_valid_variable(item) and not is_valid_field(item):
                        errors.append(f"{section_name}[{i}] is not valid (missing 'name')")
                elif section_name == 'rules':
                    if not is_valid_rule(item):
                        errors.append(f"{section_name}[{i}] is not a valid rule (missing 'name')")
    
    return errors
