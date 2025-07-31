#ifndef COMPLEX_EXAMPLE_H
#define COMPLEX_EXAMPLE_H

#include "config.h"
#include "logger.h"

/* Nested struct typedef with explicit tag */
typedef struct NestedInfo_tag {
    id_t id;
    char description[MAX_LABEL_LEN];
    log_level_t log_level;
} NestedInfo_t;

/* Enum for status with explicit tag */
typedef enum CE_Status_tag {
    CE_STATUS_OK = 0,
    CE_STATUS_WARN,
    CE_STATUS_FAIL
} CE_Status_t;

/* Main struct typedef with explicit tag */
typedef struct ComplexExample_tag {
    NestedInfo_t info;
    CE_Status_t status;
    int values[5];
} ComplexExample_t;

#endif /* COMPLEX_EXAMPLE_H */