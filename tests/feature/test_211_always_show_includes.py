from tests.framework import UnifiedTestCase


class TestAlwaysShowIncludesFeature(UnifiedTestCase):
	def test_always_show_includes(self):
		result = self.run_test("211_always_show_includes")
		self.validate_execution_success(result)
		self.validate_test_output(result)