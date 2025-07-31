#ifndef CONFIG_H
#define CONFIG_H

#include <stddef.h>
#include <stdint.h>

#define PROJECT_NAME "ComplexCProject"
#define MAX_LABEL_LEN 64
#define DEFAULT_BUFFER_SIZE 256

// Shared typedefs
typedef uint32_t id_t;
typedef int32_t status_t;

enum GlobalStatus { GS_OK, GS_ERROR, GS_UNKNOWN };
typedef enum GlobalStatus GlobalStatus_t;

#endif // CONFIG_H