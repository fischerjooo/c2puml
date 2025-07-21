#include "typedef_test.h"
#include "complex_example.h"
#include "geometry.h"
#include "logger.h"

// Global variables using typedefs
MyLen global_length = 0;
MyBuffer global_buffer;
MyComplexPtr global_complex = NULL;

// Add a function that logs buffer processing
void log_buffer(const MyBuffer* buffer) {
    if (buffer) {
        log_message(LOG_DEBUG, "Buffer length: %u, data: %s", buffer->length, buffer->data);
    }
}

// Function using typedefs
MyInt process_buffer(MyBuffer* buffer) {
    if (buffer == NULL) {
        return -1;
    }
    log_buffer(buffer);
    global_length = buffer->length;
    return 0;
}

// Callback function
int my_callback(MyBuffer* buffer) {
    return process_buffer(buffer);
}

// Function that creates complex types
MyComplex* create_complex(MyLen id, MyString name) {
    MyComplex* complex = malloc(sizeof(MyComplex));
    if (complex) {
        complex->id = id;
        complex->name = name;
        complex->callback = my_callback;
    }
    return complex;
}

// Main function
int main() {
    log_message(LOG_INFO, "Starting typedef_test main");
    MyBuffer buffer = {100, "test data"};
    MyComplex* complex = create_complex(1, "test");
    
    process_buffer(&buffer);
    
    if (complex) {
        complex->callback(&buffer);
        free(complex);
    }
    
    return 0;
}