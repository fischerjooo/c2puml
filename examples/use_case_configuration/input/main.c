#include "public.h"
#include "internal.h"

int public_function() {
    return 0;
}

int internal_function() {
    return 1;
}

struct PublicStruct {
    int x;
    int y;
};

struct InternalStruct {
    int private_data;
};

int global_public_var = 0;
int global_internal_var = 1;