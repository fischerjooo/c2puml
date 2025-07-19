#include <stdio.h>

// Valid struct
struct Valid {
    int x;
    int y;
};

// Invalid syntax - should be skipped
struct Invalid {
    int x
    int y  // missing semicolon
}

// Valid function
int main() {
    return 0;
}