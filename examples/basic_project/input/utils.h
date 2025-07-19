#ifndef UTILS_H
#define UTILS_H

#include "types.h"

// Global variables
extern int global_counter;
extern String global_name;

// Function declarations
int add(int a, int b);
float multiply(float x, float y);
void print_point(Point p);
Color get_color(int index);
Value create_value(int type, void* data);

// Struct definitions
struct Rectangle {
    Point top_left;
    Point bottom_right;
    Color color;
};

struct Circle {
    Point center;
    float radius;
    Color color;
};

// Enum definition
enum Status {
    OK = 0,
    ERROR = 1,
    WARNING = 2
};

// Union definition
union Data {
    int integer;
    float floating;
    char character;
    String string;
};

#endif // UTILS_H