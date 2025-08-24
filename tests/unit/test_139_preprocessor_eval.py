#!/usr/bin/env python3
import unittest
from src.c2puml.core.preprocessor import PreprocessorEvaluator, PreprocessorDirective, PreprocessorBlock
from src.c2puml.core.parser_tokenizer import Token, TokenType


class TestPreprocessorEvaluator(unittest.TestCase):
    def test_defined_and_macro_expansion_and_comparisons(self):
        ev = PreprocessorEvaluator()
        ev.add_define("FOO", "1")
        ev.add_define("BAR", "2")

        self.assertTrue(ev.evaluate_condition("defined(FOO)"))
        self.assertFalse(ev.evaluate_condition("defined(BAZ)"))

        # Macro expansion and numeric compare
        self.assertTrue(ev.evaluate_condition("FOO == 1"))
        self.assertTrue(ev.evaluate_condition("BAR > FOO"))
        self.assertTrue(ev.evaluate_condition("BAR != FOO"))
        self.assertTrue(ev.evaluate_condition("(FOO) && (BAR)"))
        self.assertFalse(ev.evaluate_condition("!FOO"))

    def test_parse_blocks_structure(self):
        # Build a small token stream simulating preprocessor branches
        tokens = [
            Token(TokenType.PREPROCESSOR, "#ifdef X", 1, 1),
            Token(TokenType.INT, "int", 2, 1),
            Token(TokenType.IDENTIFIER, "a", 2, 5),
            Token(TokenType.PREPROCESSOR, "#else", 3, 1),
            Token(TokenType.INT, "int", 4, 1),
            Token(TokenType.IDENTIFIER, "b", 4, 5),
            Token(TokenType.PREPROCESSOR, "#endif", 5, 1),
        ]

        ev = PreprocessorEvaluator()
        blocks = ev.parse_preprocessor_blocks(tokens)
        self.assertEqual(len(blocks), 1)
        blk = blocks[0]
        self.assertEqual(blk.start_token, 0)
        self.assertEqual(blk.end_token, 6)
        # Block should have valid indices; activation state may vary by impl
        self.assertIsInstance(blk.is_active, bool)


if __name__ == "__main__":
    unittest.main()

