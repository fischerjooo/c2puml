#include <stdio.h>
#include <string.h>
#include "complex_example.h"

#define BUFFER_SIZE 256
#define LOG_LEVEL_ERROR 3
#define LOG_LEVEL_INFO 1

// Complex struct with nested structures
typedef struct {
    int id;
    char name[64];
    struct {
        float x, y, z;
    } position;
    struct {
        unsigned char r, g, b, a;
    } color;
} entity_t;

// Union example
typedef union {
    int int_val;
    float float_val;
    char bytes[4];
} data_value_t;

// Enum with explicit values
typedef enum {
    EVENT_NONE = 0,
    EVENT_KEYBOARD = 1,
    EVENT_MOUSE = 2,
    EVENT_TIMER = 4,
    EVENT_NETWORK = 8
} event_type_t;

// Global arrays and pointers
static entity_t entities[100];
static int entity_count = 0;
entity_t* active_entity = NULL;

// Function pointer typedef
typedef void (*event_handler_t)(event_type_t type, void* data);
static event_handler_t handlers[16];

// Multi-line macro
#define SAFE_CALL(func, ...) \
    do { \
        if (func != NULL) { \
            func(__VA_ARGS__); \
        } \
    } while(0)

// Static functions
static void log_message(int level, const char* message);
static entity_t* find_entity_by_id(int id);

// Function implementations
static void log_message(int level, const char* message) {
    if (level >= LOG_LEVEL_ERROR) {
        fprintf(stderr, "[ERROR] %s\n", message);
    } else {
        printf("[INFO] %s\n", message);
    }
}

static entity_t* find_entity_by_id(int id) {
    for (int i = 0; i < entity_count; i++) {
        if (entities[i].id == id) {
            return &entities[i];
        }
    }
    return NULL;
}

int create_entity(int id, const char* name, float x, float y, float z) {
    if (entity_count >= 100) {
        log_message(LOG_LEVEL_ERROR, "Entity array full");
        return -1;
    }
    
    entity_t* entity = &entities[entity_count];
    entity->id = id;
    strncpy(entity->name, name, sizeof(entity->name) - 1);
    entity->name[sizeof(entity->name) - 1] = '\0';
    
    entity->position.x = x;
    entity->position.y = y;
    entity->position.z = z;
    
    // Default color (white)
    entity->color.r = 255;
    entity->color.g = 255;
    entity->color.b = 255;
    entity->color.a = 255;
    
    entity_count++;
    return 0;
}

void update_entity_position(int id, float x, float y, float z) {
    entity_t* entity = find_entity_by_id(id);
    if (entity != NULL) {
        entity->position.x = x;
        entity->position.y = y;
        entity->position.z = z;
    }
}

void set_entity_color(int id, unsigned char r, unsigned char g, unsigned char b, unsigned char a) {
    entity_t* entity = find_entity_by_id(id);
    if (entity != NULL) {
        entity->color.r = r;
        entity->color.g = g;
        entity->color.b = b;
        entity->color.a = a;
    }
}

void register_event_handler(event_type_t type, event_handler_t handler) {
    int index = 0;
    while (type > 1) {
        type >>= 1;
        index++;
    }
    if (index < 16) {
        handlers[index] = handler;
    }
}

void trigger_event(event_type_t type, void* data) {
    int index = 0;
    event_type_t test_type = type;
    while (test_type > 1) {
        test_type >>= 1;
        index++;
    }
    
    if (index < 16) {
        SAFE_CALL(handlers[index], type, data);
    }
}