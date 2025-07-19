#ifndef UTILS_H
#define UTILS_H

#include "types.h"

extern int global_counter;
extern char* global_name;

int add(int a, int b);
float multiply(float x, float y);
void print_point(Point p);

struct Rectangle {
    Point top_left;
    Point bottom_right;
    Color color;
};

enum Status {
    OK = 0,
    ERROR = 1,
    WARNING = 2
};

union Data {
    int integer;
    float floating;
    char character;
    char* string;
};

#endif