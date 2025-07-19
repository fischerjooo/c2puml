#!/usr/bin/env python3
"""
Integration tests for complete C to PlantUML workflow using examples

These tests use the examples from the examples folder and expectations
classes for validation, making them more reliable and maintainable.
"""

import unittest
from pathlib import Path
try:
    from tests.test_helper import UseCaseTestHelper
    from tests.expectations import (
        IntegrationWorkflowExpectations,
        ComplexExampleExpectations,
        TypedefTestExpectations,
        SampleExpectations,
        ConfigurationExpectations
    )
except ImportError:
    from .test_helper import UseCaseTestHelper
    from .expectations import (
        IntegrationWorkflowExpectations,
        ComplexExampleExpectations,
        TypedefTestExpectations,
        SampleExpectations,
        ConfigurationExpectations
    )


class TestIntegrationExamples(unittest.TestCase):
    """Integration tests for complete workflow using examples"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use examples from the examples folder
        self.examples_dir = Path(__file__).parent.parent / "examples"
    
    def test_integration_workflow_example(self):
        """Test complete workflow using the integration workflow example"""
        example_dir = self.examples_dir / "use_case_integration_workflow"
        helper = UseCaseTestHelper(IntegrationWorkflowExpectations)
        helper.run_integration_test(example_dir, self)
    
    def test_complex_example_workflow(self):
        """Test complete workflow using the complex example"""
        example_dir = self.examples_dir / "use_case_complex_example"
        helper = UseCaseTestHelper(ComplexExampleExpectations)
        helper.run_integration_test(example_dir, self)
    
    def test_typedef_test_workflow(self):
        """Test complete workflow using the typedef test example"""
        example_dir = self.examples_dir / "use_case_typedef_test"
        helper = UseCaseTestHelper(TypedefTestExpectations)
        helper.run_integration_test(example_dir, self)
    
    def test_sample_workflow(self):
        """Test complete workflow using the sample example"""
        example_dir = self.examples_dir / "use_case_sample"
        helper = UseCaseTestHelper(SampleExpectations)
        helper.run_integration_test(example_dir, self)
    
    def test_workflow_with_filtering_example(self):
        """Test workflow with filtering using the configuration example"""
        example_dir = self.examples_dir / "use_case_configuration"
        helper = UseCaseTestHelper(ConfigurationExpectations)
        helper.run_integration_test(example_dir, self)


if __name__ == '__main__':
    unittest.main()