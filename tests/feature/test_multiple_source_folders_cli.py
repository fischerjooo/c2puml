#!/usr/bin/env python3
"""
Multiple Source Folders Feature Tests via CLI
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestMultipleSourceFoldersCLI(UnifiedTestCase):
    """Validate parsing with multiple source folders using CLI"""

    def test_multiple_source_folders(self):
        result = self.run_test("multiple_source_folders_cli")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()