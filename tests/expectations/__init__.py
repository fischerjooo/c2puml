#!/usr/bin/env python3
"""
Test expectations package

This package contains expectation classes for different use cases.
Each expectation class defines the expected behavior and content
for a specific example or use case.
"""

try:
    from tests.expectations.base_expectations import BaseExpectations
    from tests.expectations.basic_project_expectations import BasicProjectExpectations
    from tests.expectations.complex_typedef_expectations import ComplexTypedefExpectations
    from tests.expectations.configuration_expectations import ConfigurationExpectations
    from tests.expectations.large_codebase_expectations import LargeCodebaseExpectations
    from tests.expectations.error_handling_expectations import ErrorHandlingExpectations
    from tests.expectations.integration_examples_expectations import (
        IntegrationWorkflowExpectations,
        ComplexExampleExpectations,
        TypedefTestExpectations,
        SampleExpectations
    )
except ImportError:
    from .base_expectations import BaseExpectations
    from .basic_project_expectations import BasicProjectExpectations
    from .complex_typedef_expectations import ComplexTypedefExpectations
    from .configuration_expectations import ConfigurationExpectations
    from .large_codebase_expectations import LargeCodebaseExpectations
    from .error_handling_expectations import ErrorHandlingExpectations
    from .integration_examples_expectations import (
        IntegrationWorkflowExpectations,
        ComplexExampleExpectations,
        TypedefTestExpectations,
        SampleExpectations
    )

__all__ = [
    'BaseExpectations',
    'BasicProjectExpectations',
    'ComplexTypedefExpectations',
    'ConfigurationExpectations',
    'LargeCodebaseExpectations',
    'ErrorHandlingExpectations',
    'IntegrationWorkflowExpectations',
    'ComplexExampleExpectations',
    'TypedefTestExpectations',
    'SampleExpectations',
]