#!/usr/bin/env python3
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from c2puml.core.preprocessor import PreprocessorEvaluator, Token, TokenType, PreprocessorManager


class TestPreprocessorEdges(unittest.TestCase):
    def test_evaluator_defined_and_macros(self):
        ev = PreprocessorEvaluator()
        ev.add_define("FOO", "1")
        ev.add_define("BAR", "2")
        self.assertTrue(ev.evaluate_condition("defined(FOO)"))
        self.assertFalse(ev.evaluate_condition("defined(BAZ)"))
        self.assertTrue(ev.evaluate_condition("FOO==1"))
        self.assertTrue(ev.evaluate_condition("BAR!=3"))
        self.assertTrue(ev.evaluate_condition("BAR>1 && FOO==1"))
        self.assertFalse(ev.evaluate_condition("BAR<1 || !FOO"))

    def test_parse_blocks_and_filter(self):
        # Create a simple token stream with #if/#endif
        toks = [
            Token(TokenType.PREPROCESSOR, "#if defined(FOO)", 1, 1),
            Token(TokenType.IDENTIFIER, "A", 1, 5),
            Token(TokenType.PREPROCESSOR, "#endif", 3, 1),
        ]
        pm = PreprocessorManager()
        pm.evaluator.add_define("FOO", "1")
        filtered = pm.evaluator.filter_tokens(toks)
        # Token 'A' should be kept
        self.assertIn("A", [t.value for t in filtered])


if __name__ == "__main__":
    unittest.main()

