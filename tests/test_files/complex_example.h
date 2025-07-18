#ifndef COMPLEX_EXAMPLE_H
#define COMPLEX_EXAMPLE_H

#define MAX_ENTITIES 100
#define ENTITY_NAME_LENGTH 64

// Forward declarations
typedef struct entity entity_t;
typedef union data_value data_value_t;
typedef enum event_type event_type_t;
typedef void (*event_handler_t)(event_type_t type, void* data);

// Function prototypes
extern int create_entity(int id, const char* name, float x, float y, float z);
extern void update_entity_position(int id, float x, float y, float z);
extern void set_entity_color(int id, unsigned char r, unsigned char g, unsigned char b, unsigned char a);
extern void register_event_handler(event_type_t type, event_handler_t handler);
extern void trigger_event(event_type_t type, void* data);

// Utility macros
#define MAKE_COLOR(r, g, b, a) \
    ((unsigned int)((a) << 24 | (r) << 16 | (g) << 8 | (b)))

#define GET_RED(color) ((color >> 16) & 0xFF)
#define GET_GREEN(color) ((color >> 8) & 0xFF)
#define GET_BLUE(color) (color & 0xFF)
#define GET_ALPHA(color) ((color >> 24) & 0xFF)

#endif // COMPLEX_EXAMPLE_H