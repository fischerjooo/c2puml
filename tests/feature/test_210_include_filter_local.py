from tests.framework import UnifiedTestCase


class TestIncludeFilterLocalOnlyFeature(UnifiedTestCase):
    def test_include_filter_local_only(self):
        result = self.run_test("210_include_filter_local")
        self.validate_execution_success(result)
        self.validate_test_output(result)