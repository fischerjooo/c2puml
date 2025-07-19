#include <stdio.h>
#include <stdlib.h>
#include "config.h"

#define MAX_SIZE 100
#define DEBUG_MODE 1

typedef int Integer;
typedef char* String;

struct Person {
    char name[50];
    int age;
    float height;
};

struct Config {
    int max_users;
    int timeout;
    String server_name;
};

enum Status {
    OK,
    ERROR,
    PENDING
};

int global_var = 42;
String global_string = "test";

int main() {
    printf("Hello, World!\n");
    return 0;
}

void process_data(void* data) {
    // Process data
}

float calculate(float a, float b) {
    return a + b;
}