#!/usr/bin/env python3

import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from c2puml.core.parser import CParser
from c2puml.core.parser_tokenizer import CTokenizer

# Test case that reproduces the network.c issue
test_code = """
#include "network.h"

void network_cleanup(NetworkConfig* config) {
    if (!config) {
        return;
    }
    
    if (config->socket_fd >= 0) {
        close(config->socket_fd);
        config->socket_fd = -1;
    }
}
"""

def test_network_parsing():
    parser = CParser()
    tokenizer = CTokenizer()
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write(test_code)
        temp_file_path = f.name
    
    try:
        # Tokenize the test code
        tokens = tokenizer.tokenize(test_code)
        print("Tokens:")
        for i, token in enumerate(tokens):
            print(f"  {i}: {token.type} = '{token.value}'")
        
        # Parse the file
        file_model = parser.parse_file(temp_file_path, "test_network.c")
        
        print(f"\nParsed file: {file_model.name}")
        print(f"Functions: {len(file_model.functions)}")
        print(f"Structs: {len(file_model.structs)}")
        print(f"Globals: {len(file_model.globals)}")
        
        # Check for any malformed fields
        for struct_name, struct_data in file_model.structs.items():
            print(f"\nStruct: {struct_name}")
            for field in struct_data.fields:
                print(f"  Field: '{field.name}' : '{field.type}'")
                if field.value:
                    print(f"    Value: '{field.value}'")
    
    finally:
        # Clean up
        os.unlink(temp_file_path)

if __name__ == "__main__":
    test_network_parsing()