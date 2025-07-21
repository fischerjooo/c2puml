#ifndef LOGGER_H
#define LOGGER_H

#include <stdio.h>
#include "config.h"

typedef enum {
    LOG_DEBUG,
    LOG_INFO,
    LOG_WARN,
    LOG_ERROR
} log_level_t;

typedef void (*log_callback_t)(log_level_t level, const char* message);

void set_log_callback(log_callback_t cb);
void log_message(log_level_t level, const char* fmt, ...);

#endif // LOGGER_H