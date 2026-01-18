"""
Custom exceptions for docassemble-dag.

Provides a hierarchy of exceptions for better error handling and user experience.
"""


class DocassembleDAGError(Exception):
    """
    Base exception for all docassemble-dag errors.
    
    All custom exceptions inherit from this for consistent error handling.
    """
    pass


class InvalidYAMLError(DocassembleDAGError):
    """
    Raised when YAML is invalid or doesn't match expected structure.
    
    Attributes:
        file_path: Optional file path where error occurred
        line_number: Optional line number where error occurred
        original_error: The original exception that caused this error
    """
    
    def __init__(
        self,
        message: str,
        file_path: str = None,
        line_number: int = None,
        original_error: Exception = None,
    ):
        super().__init__(message)
        self.file_path = file_path
        self.line_number = line_number
        self.original_error = original_error


class ParsingError(DocassembleDAGError):
    """
    Raised when parsing fails.
    
    Attributes:
        file_path: Optional file path where parsing failed
        line_number: Optional line number where parsing failed
        original_error: The original exception that caused this error
    """
    
    def __init__(
        self,
        message: str,
        file_path: str = None,
        line_number: int = None,
        original_error: Exception = None,
    ):
        super().__init__(message)
        self.file_path = file_path
        self.line_number = line_number
        self.original_error = original_error


class GraphError(DocassembleDAGError):
    """
    Raised when graph operations fail.
    
    Attributes:
        node_name: Optional node name related to the error
    """
    
    def __init__(self, message: str, node_name: str = None):
        super().__init__(message)
        self.node_name = node_name


class CycleError(GraphError):
    """
    Raised when cycles are detected where they shouldn't be.
    
    Attributes:
        cycles: List of cycles found
    """
    
    def __init__(self, message: str, cycles: list = None):
        super().__init__(message)
        self.cycles = cycles or []


class ValidationError(DocassembleDAGError):
    """
    Raised when validation fails.
    
    Attributes:
        violations: List of validation violations
    """
    
    def __init__(self, message: str, violations: list = None):
        super().__init__(message)
        self.violations = violations or []


class StorageError(DocassembleDAGError):
    """
    Raised when graph storage operations fail.
    
    Attributes:
        operation: The storage operation that failed
        original_error: The original exception that caused this error
    """
    
    def __init__(self, message: str, operation: str = None, original_error: Exception = None):
        super().__init__(message)
        self.operation = operation
        self.original_error = original_error
