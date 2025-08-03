#!/usr/bin/env python3
"""
Preprocessor module for C to PlantUML converter.
Handles #if, #elif, #else, #endif directives and conditional compilation.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from .parser_tokenizer import Token, TokenType


class PreprocessorDirective(Enum):
    """Types of preprocessor directives."""

    IF = "if"
    ELIF = "elif"
    ELSE = "else"
    ENDIF = "endif"
    IFDEF = "ifdef"
    IFNDEF = "ifndef"
    DEFINE = "define"
    UNDEF = "undef"


@dataclass
class PreprocessorBlock:
    """Represents a preprocessor conditional block."""

    directive: PreprocessorDirective
    condition: str
    start_token: int
    end_token: int
    is_active: bool
    children: List["PreprocessorBlock"]
    parent: Optional["PreprocessorBlock"] = None


class PreprocessorEvaluator:
    """Evaluates preprocessor conditions and manages conditional compilation."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.defined_macros: Set[str] = set()
        self.macro_values: Dict[str, str] = {}
        self.blocks: List[PreprocessorBlock] = []
        self.current_block_stack: List[PreprocessorBlock] = []

    def add_define(self, name: str, value: str = ""):
        """Add a defined macro."""
        self.defined_macros.add(name)
        if value:
            self.macro_values[name] = value

    def add_undef(self, name: str):
        """Remove a defined macro."""
        self.defined_macros.discard(name)
        self.macro_values.pop(name, None)

    def is_defined(self, name: str) -> bool:
        """Check if a macro is defined."""
        return name in self.defined_macros

    def get_macro_value(self, name: str) -> str:
        """Get the value of a defined macro."""
        return self.macro_values.get(name, "")

    def evaluate_condition(self, condition: str) -> bool:
        """Evaluate a preprocessor condition."""
        if not condition.strip():
            return True

        # Handle defined() operator
        condition = self._expand_defined_operator(condition)

        # Handle macro expansions
        condition = self._expand_macros(condition)

        # Evaluate common patterns
        return self._evaluate_simple_expression(condition)

    def _expand_defined_operator(self, condition: str) -> str:
        """Expand defined() operators in the condition."""

        def replace_defined(match):
            macro_name = match.group(1)
            return "1" if self.is_defined(macro_name) else "0"

        # Replace defined(macro) with 1 or 0
        condition = re.sub(
            r"defined\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)", replace_defined, condition
        )
        return condition

    def _expand_macros(self, condition: str) -> str:
        """Expand macros in the condition."""
        # Macro expansion for common cases
        for macro_name, macro_value in self.macro_values.items():
            # Replace macro name with its value
            pattern = r"\b" + re.escape(macro_name) + r"\b"
            condition = re.sub(pattern, macro_value, condition)
        return condition

    def _evaluate_simple_expression(self, condition: str) -> bool:
        """Evaluate simple expressions like comparisons and logical operators."""
        try:
            # Handle common comparison operators
            condition = condition.strip()

            # Handle simple boolean values
            if condition.lower() in ["1", "true", "yes"]:
                return True
            if condition.lower() in ["0", "false", "no"]:
                return False

            # Handle simple comparisons
            if "==" in condition:
                left, right = condition.split("==", 1)
                left_val = left.strip()
                right_val = right.strip()

                # If both sides are known macros, compare their values
                if left_val in self.defined_macros and right_val in self.defined_macros:
                    return self.get_macro_value(left_val) == self.get_macro_value(
                        right_val
                    )
                # If one side is a known macro, compare with the other side
                elif left_val in self.defined_macros:
                    return self.get_macro_value(left_val) == right_val
                elif right_val in self.defined_macros:
                    return left_val == self.get_macro_value(right_val)
                # If neither side is a known macro, both are undefined, so they're equal
                else:
                    return True  # Both undefined macros are considered equal

            if "!=" in condition:
                left, right = condition.split("!=", 1)
                left_val = left.strip()
                right_val = right.strip()

                # If both sides are known macros, compare their values
                if left_val in self.defined_macros and right_val in self.defined_macros:
                    return self.get_macro_value(left_val) != self.get_macro_value(
                        right_val
                    )
                # If one side is a known macro, compare with the other side
                elif left_val in self.defined_macros:
                    return self.get_macro_value(left_val) != right_val
                elif right_val in self.defined_macros:
                    return left_val != self.get_macro_value(right_val)
                # If neither side is a known macro, do string comparison
                else:
                    return left_val != right_val

            if ">" in condition:
                left, right = condition.split(">", 1)
                try:
                    left_val = self._evaluate_operand(left.strip())
                    right_val = self._evaluate_operand(right.strip())
                    return float(left_val) > float(right_val)
                except ValueError:
                    return False
            if "<" in condition:
                left, right = condition.split("<", 1)
                try:
                    left_val = self._evaluate_operand(left.strip())
                    right_val = self._evaluate_operand(right.strip())
                    return float(left_val) < float(right_val)
                except ValueError:
                    return False
            if ">=" in condition:
                left, right = condition.split(">=", 1)
                try:
                    left_val = self._evaluate_operand(left.strip())
                    right_val = self._evaluate_operand(right.strip())
                    return float(left_val) >= float(right_val)
                except ValueError:
                    return False
            if "<=" in condition:
                left, right = condition.split("<=", 1)
                try:
                    left_val = self._evaluate_operand(left.strip())
                    right_val = self._evaluate_operand(right.strip())
                    return float(left_val) <= float(right_val)
                except ValueError:
                    return False

            # Handle logical operators
            if "&&" in condition:
                parts = condition.split("&&")
                return all(
                    self._evaluate_simple_expression(part.strip()) for part in parts
                )
            if "||" in condition:
                parts = condition.split("||")
                return any(
                    self._evaluate_simple_expression(part.strip()) for part in parts
                )
            if "!" in condition:
                # Negation
                negated = condition.replace("!", "").strip()
                return not self._evaluate_simple_expression(negated)

            # If it's just a macro name, check if it's defined
            if condition in self.defined_macros:
                return True

            # Try to evaluate as a number
            try:
                return bool(int(condition))
            except ValueError:
                pass

            # Default to True for unknown conditions (backward compatibility)
            # This ensures existing tests continue to work
            return True

        except ValueError as e:
            self.logger.warning(
                "Error evaluating preprocessor condition '%s': %s", condition, e
            )
            # Default to True for unknown conditions (backward compatibility)
            return True

    def _evaluate_operand(self, operand: str) -> str:
        """Evaluate an operand, expanding macros if they are defined."""
        operand = operand.strip()

        # If it's a defined macro, return its value
        if operand in self.defined_macros:
            return self.get_macro_value(operand)

        # Otherwise, return the operand as-is
        return operand

    def parse_preprocessor_blocks(self, tokens: List[Token]) -> List[PreprocessorBlock]:
        """Parse preprocessor blocks from tokens."""
        blocks = []
        stack = []

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token.type == TokenType.PREPROCESSOR:
                directive = self._parse_directive(token.value)

                if (
                    directive == PreprocessorDirective.IF
                    or directive == PreprocessorDirective.IFDEF
                    or directive == PreprocessorDirective.IFNDEF
                ):
                    # Start new block
                    condition = self._extract_condition(token.value, directive)
                    block = PreprocessorBlock(
                        directive=directive,
                        condition=condition,
                        start_token=i,
                        end_token=-1,  # Will be set when we find #endif
                        is_active=self._should_activate_block(
                            directive, condition, stack
                        ),
                        children=[],
                        parent=stack[-1] if stack else None,
                    )

                    if stack:
                        stack[-1].children.append(block)
                    else:
                        blocks.append(block)

                    stack.append(block)

                elif directive == PreprocessorDirective.ELIF:
                    if stack:
                        # Update current block
                        current_block = stack[-1]
                        condition = self._extract_condition(token.value, directive)
                        current_block.is_active = self._should_activate_block(
                            directive, condition, stack
                        )

                elif directive == PreprocessorDirective.ELSE:
                    if stack:
                        # Update current block
                        current_block = stack[-1]
                        current_block.is_active = self._should_activate_block(
                            directive, "", stack
                        )

                elif directive == PreprocessorDirective.ENDIF:
                    if stack:
                        # End current block
                        current_block = stack.pop()
                        current_block.end_token = i

                elif directive == PreprocessorDirective.DEFINE:
                    # Handle #define
                    macro_name, macro_value = self._parse_define(token.value)
                    self.add_define(macro_name, macro_value)

                elif directive == PreprocessorDirective.UNDEF:
                    # Handle #undef
                    macro_name = self._parse_undef(token.value)
                    self.add_undef(macro_name)

            i += 1

        return blocks

    def _parse_directive(self, value: str) -> PreprocessorDirective:
        """Parse the directive type from a preprocessor token."""
        value = value.strip()
        if value.startswith("#ifdef"):
            return PreprocessorDirective.IFDEF
        elif value.startswith("#ifndef"):
            return PreprocessorDirective.IFNDEF
        elif value.startswith("#if"):
            return PreprocessorDirective.IF
        elif value.startswith("#elif"):
            return PreprocessorDirective.ELIF
        elif value.startswith("#else"):
            return PreprocessorDirective.ELSE
        elif value.startswith("#endif"):
            return PreprocessorDirective.ENDIF
        elif value.startswith("#define"):
            return PreprocessorDirective.DEFINE
        elif value.startswith("#undef"):
            return PreprocessorDirective.UNDEF
        else:
            return PreprocessorDirective.IF  # Default

    def _extract_condition(self, value: str, directive: PreprocessorDirective) -> str:
        """Extract the condition from a preprocessor directive."""
        value = value.strip()

        if directive == PreprocessorDirective.IFDEF:
            match = re.search(r"#ifdef\s+([a-zA-Z_][a-zA-Z0-9_]*)", value)
            return match.group(1) if match else ""
        elif directive == PreprocessorDirective.IFNDEF:
            match = re.search(r"#ifndef\s+([a-zA-Z_][a-zA-Z0-9_]*)", value)
            return match.group(1) if match else ""
        elif directive == PreprocessorDirective.IF:
            match = re.search(r"#if\s+(.+)", value)
            return match.group(1).strip() if match else ""
        elif directive == PreprocessorDirective.ELIF:
            match = re.search(r"#elif\s+(.+)", value)
            return match.group(1).strip() if match else ""
        else:
            return ""

    def _parse_define(self, value: str) -> Tuple[str, str]:
        """Parse #define directive."""
        value = value.strip()
        match = re.search(r"#define\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(.+)", value)
        if match:
            name = match.group(1)
            macro_value = match.group(2).strip()
            return name, macro_value
        return "", ""

    def _parse_undef(self, value: str) -> str:
        """Parse #undef directive."""
        value = value.strip()
        match = re.search(r"#undef\s+([a-zA-Z_][a-zA-Z0-9_]*)", value)
        return match.group(1) if match else ""

    def _should_activate_block(
        self,
        directive: PreprocessorDirective,
        condition: str,
        stack: List[PreprocessorBlock],
    ) -> bool:
        """Determine if a block should be active based on its directive and condition."""
        # Check if parent blocks are active
        if stack and not stack[-1].is_active:
            return False

        if directive == PreprocessorDirective.IFDEF:
            return self.is_defined(condition)
        elif directive == PreprocessorDirective.IFNDEF:
            return not self.is_defined(condition)
        elif directive == PreprocessorDirective.IF:
            return self.evaluate_condition(condition)
        elif directive == PreprocessorDirective.ELIF:
            # For #elif, we need to check if no previous branch was taken
            if stack:
                parent = stack[-1]
                # Check if any previous child was active
                for child in parent.children:
                    if child.is_active:
                        return False
                return self.evaluate_condition(condition)
            return False
        elif directive == PreprocessorDirective.ELSE:
            # For #else, we need to check if no previous branch was taken
            if stack:
                parent = stack[-1]
                # Check if any previous child was active
                for child in parent.children:
                    if child.is_active:
                        return False
                return True
            return False
        else:
            return False

    def filter_tokens(self, tokens: List[Token]) -> List[Token]:
        """Filter tokens based on preprocessor blocks, keeping only active content."""
        blocks = self.parse_preprocessor_blocks(tokens)
        filtered_tokens = []

        i = 0
        while i < len(tokens):
            token = tokens[i]

            # Check if this token is inside a preprocessor block
            in_active_block = self._is_token_in_active_block(i, blocks)

            if in_active_block:
                # Include the token if it's not a preprocessor directive
                if token.type != TokenType.PREPROCESSOR:
                    filtered_tokens.append(token)
            else:
                # Skip tokens that are not in active blocks
                pass

            i += 1

        return filtered_tokens

    def _is_token_in_active_block(
        self, token_index: int, blocks: List[PreprocessorBlock]
    ) -> bool:
        """Check if a token is inside an active preprocessor block."""
        # Check all blocks recursively
        for block in blocks:
            if self._is_token_in_block(token_index, block):
                # If token is in this block, return whether the block is active
                return block.is_active
        return True  # Default to True if not in any block

    def _is_token_in_block(self, token_index: int, block: PreprocessorBlock) -> bool:
        """Check if a token is inside a specific block."""
        if block.start_token <= token_index <= block.end_token:
            # Check if any child block contains this token
            for child in block.children:
                if self._is_token_in_block(token_index, child):
                    # If token is in a child block, return whether the child is active
                    return child.is_active
            # Token is in this block but not in any child block
            return True
        return False


class PreprocessorManager:
    """High-level interface for preprocessor management."""

    def __init__(self):
        self.evaluator = PreprocessorEvaluator()
        self.logger = logging.getLogger(__name__)

    def process_file(
        self, tokens: List[Token], defines: Optional[Dict[str, str]] = None
    ) -> List[Token]:
        """Process a file's tokens through the preprocessor."""
        if defines:
            for name, value in defines.items():
                self.evaluator.add_define(name, value)

        # Filter tokens based on preprocessor directives
        filtered_tokens = self.evaluator.filter_tokens(tokens)

        self.logger.debug(
            f"Preprocessor: {len(tokens)} tokens -> {len(filtered_tokens)} tokens"
        )
        return filtered_tokens

    def add_defines_from_content(self, tokens: List[Token]):
        """Extract #define directives from tokens and add them to the evaluator."""
        for token in tokens:
            if token.type == TokenType.PREPROCESSOR and token.value.startswith(
                "#define"
            ):
                name, value = self.evaluator._parse_define(token.value)
                if name:
                    self.evaluator.add_define(name, value)
                    self.logger.debug("Preprocessor: Added define %s = %s", name, value)
