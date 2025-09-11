from tests.framework import UnifiedTestCase


class TestIncludeDepthLimit(UnifiedTestCase):
    def test_include_depth_limit(self):
        result = self.run_test("142_include_depth_limit")
        self.validate_execution_success(result)
        self.validate_test_output(result)

