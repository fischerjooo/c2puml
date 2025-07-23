#!/usr/bin/env python3
"""
Centralized error handling module for C to PlantUML converter.

This module provides custom exceptions, error codes, and context logging
to ensure clear, consistent error messages for users and easier debugging
for maintainers.
"""

import logging
import traceback
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class ErrorCode(Enum):
    """Error codes for different types of failures."""
    
    # Parser errors (1000-1999)
    PARSER_FILE_NOT_FOUND = 1000
    PARSER_INVALID_ENCODING = 1001
    PARSER_SYNTAX_ERROR = 1002
    PARSER_TOKENIZATION_ERROR = 1003
    PARSER_INCLUDE_NOT_FOUND = 1004
    PARSER_PREPROCESSOR_ERROR = 1005
    PARSER_MALFORMED_STRUCT = 1006
    PARSER_MALFORMED_ENUM = 1007
    PARSER_MALFORMED_UNION = 1008
    PARSER_MALFORMED_FUNCTION = 1009
    PARSER_MALFORMED_TYPEDEF = 1010
    
    # Transformer errors (2000-2999)
    TRANSFORMER_INVALID_CONFIG = 2000
    TRANSFORMER_FILTER_ERROR = 2001
    TRANSFORMER_VALIDATION_ERROR = 2002
    TRANSFORMER_DEPENDENCY_ERROR = 2003
    
    # Generator errors (3000-3999)
    GENERATOR_OUTPUT_ERROR = 3000
    GENERATOR_TEMPLATE_ERROR = 3001
    GENERATOR_FORMAT_ERROR = 3002
    GENERATOR_WRITE_ERROR = 3003
    
    # Configuration errors (4000-4999)
    CONFIG_INVALID_FILE = 4000
    CONFIG_INVALID_SCHEMA = 4001
    CONFIG_MISSING_REQUIRED = 4002
    CONFIG_INVALID_VALUE = 4003
    
    # Verification errors (5000-5999)
    VERIFIER_SANITY_CHECK_FAILED = 5000
    VERIFIER_MODEL_INVALID = 5001
    VERIFIER_CONSISTENCY_ERROR = 5002
    
    # System errors (9000-9999)
    SYSTEM_IO_ERROR = 9000
    SYSTEM_PERMISSION_ERROR = 9001
    SYSTEM_MEMORY_ERROR = 9002
    SYSTEM_UNKNOWN_ERROR = 9999


class CToPlantUMLError(Exception):
    """Base exception for all C to PlantUML converter errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.original_exception = original_exception
        self.timestamp = None
        
        # Build the full error message
        full_message = f"[{error_code.name}] {message}"
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            full_message += f" (Context: {context_str})"
        
        super().__init__(full_message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "error_code": self.error_code.name,
            "error_code_value": self.error_code.value,
            "message": self.message,
            "context": self.context,
            "original_exception": str(self.original_exception) if self.original_exception else None,
            "timestamp": self.timestamp,
        }


class ParserError(CToPlantUMLError):
    """Exception raised for parser-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        file_path: Optional[Union[str, Path]] = None,
        line_number: Optional[int] = None,
        column_number: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        context = context or {}
        if file_path:
            context["file_path"] = str(file_path)
        if line_number is not None:
            context["line_number"] = line_number
        if column_number is not None:
            context["column_number"] = column_number
        
        super().__init__(message, error_code, context, original_exception)


class TransformerError(CToPlantUMLError):
    """Exception raised for transformer-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        transformation_step: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        context = context or {}
        if transformation_step:
            context["transformation_step"] = transformation_step
        
        super().__init__(message, error_code, context, original_exception)


class GeneratorError(CToPlantUMLError):
    """Exception raised for generator-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        output_path: Optional[Union[str, Path]] = None,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        context = context or {}
        if output_path:
            context["output_path"] = str(output_path)
        if template_name:
            context["template_name"] = template_name
        
        super().__init__(message, error_code, context, original_exception)


class ConfigError(CToPlantUMLError):
    """Exception raised for configuration-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        config_path: Optional[Union[str, Path]] = None,
        config_key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        context = context or {}
        if config_path:
            context["config_path"] = str(config_path)
        if config_key:
            context["config_key"] = config_key
        
        super().__init__(message, error_code, context, original_exception)


class VerifierError(CToPlantUMLError):
    """Exception raised for verification-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        verification_step: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        context = context or {}
        if verification_step:
            context["verification_step"] = verification_step
        
        super().__init__(message, error_code, context, original_exception)


class ErrorHandler:
    """Centralized error handler with logging and context management."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_count = 0
        self.warning_count = 0
        self.errors: List[CToPlantUMLError] = []
        self.warnings: List[str] = []
    
    def handle_error(
        self,
        error: CToPlantUMLError,
        raise_exception: bool = True,
        log_level: int = logging.ERROR,
    ) -> None:
        """Handle an error with logging and optional exception raising."""
        self.error_count += 1
        self.errors.append(error)
        
        # Log the error with context
        self.logger.log(
            log_level,
            f"Error {self.error_count}: {error.message}",
            extra={
                "error_code": error.error_code.name,
                "error_code_value": error.error_code.value,
                "context": error.context,
                "original_exception": error.original_exception,
            }
        )
        
        if raise_exception:
            raise error
    
    def handle_warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        log_level: int = logging.WARNING,
    ) -> None:
        """Handle a warning with logging."""
        self.warning_count += 1
        self.warnings.append(message)
        
        # Log the warning with context
        self.logger.log(
            log_level,
            f"Warning {self.warning_count}: {message}",
            extra={"context": context} if context else {}
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all errors and warnings."""
        return {
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "errors": [error.to_dict() for error in self.errors],
            "warnings": self.warnings,
        }
    
    def clear(self) -> None:
        """Clear all errors and warnings."""
        self.error_count = 0
        self.warning_count = 0
        self.errors.clear()
        self.warnings.clear()


def create_error_context(
    file_path: Optional[Union[str, Path]] = None,
    line_number: Optional[int] = None,
    column_number: Optional[int] = None,
    function_name: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Create a standardized error context dictionary."""
    context = {}
    
    if file_path:
        context["file_path"] = str(file_path)
    if line_number is not None:
        context["line_number"] = line_number
    if column_number is not None:
        context["column_number"] = column_number
    if function_name:
        context["function_name"] = function_name
    
    # Add any additional context
    context.update(kwargs)
    
    return context


def wrap_exception(
    exception: Exception,
    error_code: ErrorCode,
    message: str,
    context: Optional[Dict[str, Any]] = None,
) -> CToPlantUMLError:
    """Wrap an existing exception with C to PlantUML error context."""
    if isinstance(exception, CToPlantUMLError):
        return exception
    
    return CToPlantUMLError(
        message=message,
        error_code=error_code,
        context=context,
        original_exception=exception,
    )


# Global error handler instance
_global_error_handler = ErrorHandler()


def get_global_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    return _global_error_handler


def set_global_error_handler(handler: ErrorHandler) -> None:
    """Set the global error handler instance."""
    global _global_error_handler
    _global_error_handler = handler