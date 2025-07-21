#include "logger.h"
#include <stdarg.h>
#include <string.h>

static log_callback_t current_cb = NULL;

void set_log_callback(log_callback_t cb) {
    current_cb = cb;
}

void log_message(log_level_t level, const char* fmt, ...) {
    char buffer[256];
    va_list args;
    va_start(args, fmt);
    vsnprintf(buffer, sizeof(buffer), fmt, args);
    va_end(args);
    if (current_cb) {
        current_cb(level, buffer);
    } else {
        const char* level_str = "UNKNOWN";
        switch (level) {
            case LOG_DEBUG: level_str = "DEBUG"; break;
            case LOG_INFO: level_str = "INFO"; break;
            case LOG_WARN: level_str = "WARN"; break;
            case LOG_ERROR: level_str = "ERROR"; break;
        }
        printf("[%s] %s\n", level_str, buffer);
    }
}