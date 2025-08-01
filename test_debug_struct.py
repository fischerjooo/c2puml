#!/usr/bin/env python3

import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from c2puml.core.parser import CParser
from c2puml.core.parser_tokenizer import CTokenizer, StructureFinder

# Test case that reproduces the issue
test_code = """
#include "network.h"

int network_connect(NetworkConfig* config, const char* host, int port) {
    if (!config || !host) {
        return -1;
    }
    
    config->socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (config->socket_fd < 0) {
        return -1;
    }
    
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    
    if (inet_pton(AF_INET, host, &server_addr.sin_addr) <= 0) {
        close(config->socket_fd);
        config->socket_fd = -1;
        return -1;
    }
    
    if (connect(config->socket_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        close(config->socket_fd);
        config->socket_fd = -1;
        return -1;
    }
    
    return 0;
}
"""

def test_debug_struct():
    parser = CParser()
    tokenizer = CTokenizer()
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write(test_code)
        temp_file_path = f.name
    
    try:
        # Tokenize the test code
        tokens = tokenizer.tokenize(test_code)
        print("All tokens:")
        for i, token in enumerate(tokens):
            print(f"  {i}: {token.type} = '{token.value}'")
        
        # Use StructureFinder directly to see what it finds
        structure_finder = StructureFinder(tokens)
        structs = structure_finder.find_structs()
        print(f"\nStructureFinder found {len(structs)} structs:")
        for start_pos, end_pos, struct_name in structs:
            print(f"  Struct: '{struct_name}' from pos {start_pos} to {end_pos}")
            print(f"  Tokens in range:")
            for i in range(start_pos, min(end_pos + 1, len(tokens))):
                print(f"    {i}: {tokens[i].type} = '{tokens[i].value}'")
            print()
        
        # Parse the file
        file_model = parser.parse_file(temp_file_path, "test_debug.c")
        
        print(f"\nParsed file: {file_model.name}")
        print(f"Functions: {len(file_model.functions)}")
        print(f"Structs: {len(file_model.structs)}")
        print(f"Globals: {len(file_model.globals)}")
        
        # Check for any malformed structs
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
    test_debug_struct()