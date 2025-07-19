#include "types.h"

Integer global_integer = 42;
Vector3D global_vector = {1, 2, 3};
Color global_color = {1.0, 0.5, 0.0, 1.0};
State global_state = STATE_RUNNING;

Integer add_integers(Integer a, Integer b) {
    return a + b;
}

Vector3D create_vector(Integer x, Integer y, Integer z) {
    Vector3D v = {x, y, z};
    return v;
}

int main() {
    Integer x = 10;
    Float y = 3.14;
    Vector3D pos = create_vector(1, 2, 3);
    Color col = global_color;
    
    return 0;
}