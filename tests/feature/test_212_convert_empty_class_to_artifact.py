#!/usr/bin/env python3
import os
import unittest

from tests.framework import UnifiedTestCase


class TestConvertEmptyClassToArtifact(UnifiedTestCase):
    def test_convert_empty_class_to_artifact(self):
        result = self.run_test("212_convert_empty_class_to_artifact")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()

