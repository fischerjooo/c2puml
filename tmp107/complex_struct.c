typedef struct {
    int base_id;
    struct {
        char name[64];
        float value;
        struct {
            int x, y, z;
        } coordinates;
    } metadata;
    union {
        long long_value;
        double double_value;
    } data_variant;
    char buffer[256];
} complex_struct_t;

void init_complex_struct(complex_struct_t* cs) {
    cs->base_id = 0;
    cs->metadata.value = 0.0f;
}

complex_struct_t global_complex;
