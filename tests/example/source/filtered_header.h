#ifndef FILTERED_HEADER_H
#define FILTERED_HEADER_H

#include <stdio.h>
#include <stdlib.h>

/* This header should be filtered out by include_filters */
#define FILTERED_CONSTANT 42
#define FILTERED_MACRO(x) ((x) * 2)

/* Filtered struct that should not appear in PlantUML */
typedef struct {
    int filtered_field1;
    char filtered_field2[50];
    double filtered_field3;
} filtered_struct_t;

/* Filtered enum that should not appear in PlantUML */
typedef enum {
    FILTERED_VALUE_1 = 1,
    FILTERED_VALUE_2 = 2,
    FILTERED_VALUE_3 = 3
} filtered_enum_t;

/* Filtered function declarations that should not appear in PlantUML */
int filtered_function1(int param);
void filtered_function2(const char* message);
double filtered_function3(filtered_struct_t* data);

/* Filtered global variables that should not appear in PlantUML */
extern int filtered_global_var;
extern char filtered_global_string[100];

#endif /* FILTERED_HEADER_H */