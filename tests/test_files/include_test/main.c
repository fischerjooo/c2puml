#include <stdio.h>
#include <stdlib.h>
#include "utils.h"
#include "config.h"
#include "types.h"

typedef int Integer;
typedef char* String;
typedef void (*Callback)(int);

struct Person {
    char* name;
    int age;
    Integer id;
};

enum Status {
    OK,
    ERROR,
    PENDING
};

int global_var = 42;
char* global_string = "hello";

int main() {
    printf("Hello, World!\n");
    return 0;
}

void process_data() {
    // Function implementation
}

float calculate() {
    return 3.14f;
}