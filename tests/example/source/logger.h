#ifndef LOGGER_H
#define LOGGER_H

#include <stdio.h>
#include "config.h"

/* Log level enum with explicit tag */
typedef enum log_level_tag {
    LOG_DEBUG = 0,
    LOG_INFO,
    LOG_WARN,
    LOG_ERROR
} log_level_t;

/* Function pointer typedef for log callback */
typedef void (*log_callback_t)(log_level_t level, const char * message);

void set_log_callback(log_callback_t cb);
void log_message(log_level_t level, const char * fmt, ...);

#endif /* LOGGER_H */