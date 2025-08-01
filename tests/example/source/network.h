#ifndef NETWORK_H
#define NETWORK_H

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>
#include "common.h"

#define MAX_CONNECTIONS 100
#define DEFAULT_PORT 8080

typedef struct {
    int socket_fd;
    struct sockaddr_in address;
    int port;
    char* hostname;
} NetworkConfig;

typedef enum {
    NET_STATUS_DISCONNECTED,
    NET_STATUS_CONNECTING,
    NET_STATUS_CONNECTED,
    NET_STATUS_ERROR
} NetworkStatus;

// Network initialization and cleanup
int network_init(NetworkConfig* config);
void network_cleanup(NetworkConfig* config);

// Connection management
int network_connect(NetworkConfig* config, const char* host, int port);
int network_listen(NetworkConfig* config, int port);
int network_accept(NetworkConfig* config);
void network_disconnect(NetworkConfig* config);

// Data transfer
ssize_t network_send(int socket_fd, const void* data, size_t size);
ssize_t network_receive(int socket_fd, void* buffer, size_t size);

// Status and utilities
NetworkStatus network_get_status(const NetworkConfig* config);
const char* network_status_string(NetworkStatus status);
int network_set_nonblocking(int socket_fd);

#endif // NETWORK_H