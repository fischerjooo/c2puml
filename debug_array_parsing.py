#!/usr/bin/env python3

from c_to_plantuml.parser import CParser
from c_to_plantuml.parser_tokenizer import CTokenizer, TokenType

# Test array declaration parsing
content = """char buffer[MAX_SIZE];"""

tokenizer = CTokenizer()
tokens = tokenizer.tokenize(content)
filtered_tokens = tokenizer.filter_tokens(tokens)

print("=== Array Declaration Test ===")
print("Content:", content)
print("Filtered tokens:")
for i, token in enumerate(filtered_tokens):
    print(f"  {i}: {token}")

# Test the global parsing logic
parser = CParser()
global_info = parser._parse_global_variable(filtered_tokens, 0)
print(f"\nGlobal parsing result: {global_info}")

# Test the array detection logic
collected_tokens = []
for token in filtered_tokens:
    if token.type != TokenType.SEMICOLON:
        if token.type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
            collected_tokens.append(token)

print(f"\nCollected tokens: {[t.value for t in collected_tokens]}")

# Test bracket detection
bracket_idx = None
for j in range(len(collected_tokens) - 1, -1, -1):
    if collected_tokens[j].type == TokenType.RBRACKET:
        bracket_idx = j
        break

print(f"Bracket index: {bracket_idx}")

if bracket_idx is not None:
    # Find identifier before opening bracket
    for j in range(bracket_idx - 1, -1, -1):
        if collected_tokens[j].type == TokenType.LBRACKET:
            # Found opening bracket, look for identifier before it
            for k in range(j - 1, -1, -1):
                if collected_tokens[k].type == TokenType.IDENTIFIER:
                    var_name = collected_tokens[k].value
                    type_tokens = collected_tokens[:k]
                    var_type = ' '.join(t.value for t in type_tokens)
                    print(f"Found array: name='{var_name}', type='{var_type}'")
                    break
            break