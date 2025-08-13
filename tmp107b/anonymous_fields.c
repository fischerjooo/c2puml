typedef struct {
    int id;
    struct {
        char label[32];
        union {
            int int_val;
            float float_val;
        };  // Anonymous union within anonymous struct
        double precision;
    } config;  // Named anonymous struct field
    union {
        struct {
            int width;
            int height;
        } dimensions;  // Named struct within anonymous union
        long area;
    };  // Anonymous union
} container_t;

void setup_container(container_t* c) {
    c->id = 1;
    c->config.precision = 1.0;
    c->dimensions.width = 800;
}

container_t global_container = {0};
