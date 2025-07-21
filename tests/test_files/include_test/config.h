#ifndef CONFIG_H
#define CONFIG_H

#include <stdint.h>

typedef uint32_t ConfigId;
typedef uint16_t PortNumber;
typedef char* ConfigString;

#define DEFAULT_PORT 8080
#define MAX_CONNECTIONS 1000
#define CONFIG_VERSION "1.0"

extern ConfigId current_config_id;
extern PortNumber server_port;

struct Config {
    ConfigId id;
    ConfigString name;
    PortNumber port;
};

#endif // CONFIG_H