#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from c2puml.core.parser import CParser
from c2puml.core.parser_tokenizer import CTokenizer
from c2puml.core.preprocessor import PreprocessorManager

# Test case that reproduces the issue
test_code = """
#include <stdio.h>

// Simple global
int simple_global = 42;

// Complex global with function pointer array initializer
typedef int (*func_ptr_t)(int);
func_ptr_t complex_global[] = {
    &function1,
    &function2,
    &function3,
};

// Another complex case
Process_Cfg_Process_acpfct_t Process_Cfg_Process_acpfct = {
    &ProcessorAdapter_Process,
    &ProcessorService_Process,
    &ProcessorHardware_Process,
};
"""

def test_global_parsing():
    parser = CParser()
    tokenizer = CTokenizer()
    preprocessor = PreprocessorManager()
    
    # Tokenize the test code
    tokens = tokenizer.tokenize(test_code)
    print("Tokens:")
    for i, token in enumerate(tokens[:20]):  # Show first 20 tokens
        print(f"  {i}: {token.type} = '{token.value}'")
    
    # Parse globals
    globals_list = parser._parse_globals_with_tokenizer(tokens)
    print(f"\nParsed globals ({len(globals_list)}):")
    for global_var in globals_list:
        print(f"  Name: '{global_var.name}'")
        print(f"  Type: '{global_var.type}'")
        print(f"  Value: '{global_var.value}'")
        print()

if __name__ == "__main__":
    test_global_parsing()