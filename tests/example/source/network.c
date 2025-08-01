#include "network.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>

int network_init(NetworkConfig* config) {
    if (!config) {
        return -1;
    }
    
    memset(config, 0, sizeof(NetworkConfig));
    config->socket_fd = -1;
    config->port = DEFAULT_PORT;
    
    return 0;
}

void network_cleanup(NetworkConfig* config) {
    if (!config) {
        return;
    }
    
    if (config->socket_fd >= 0) {
        close(config->socket_fd);
        config->socket_fd = -1;
    }
    
    if (config->hostname) {
        free(config->hostname);
        config->hostname = NULL;
    }
}

int network_connect(NetworkConfig* config, const char* host, int port) {
    if (!config || !host) {
        return -1;
    }
    
    config->socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (config->socket_fd < 0) {
        return -1;
    }
    
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    
    if (inet_pton(AF_INET, host, &server_addr.sin_addr) <= 0) {
        close(config->socket_fd);
        config->socket_fd = -1;
        return -1;
    }
    
    if (connect(config->socket_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        close(config->socket_fd);
        config->socket_fd = -1;
        return -1;
    }
    
    config->port = port;
    config->hostname = strdup(host);
    config->address = server_addr;
    
    return 0;
}

int network_listen(NetworkConfig* config, int port) {
    if (!config) {
        return -1;
    }
    
    config->socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (config->socket_fd < 0) {
        return -1;
    }
    
    int opt = 1;
    if (setsockopt(config->socket_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        close(config->socket_fd);
        config->socket_fd = -1;
        return -1;
    }
    
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);
    
    if (bind(config->socket_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        close(config->socket_fd);
        config->socket_fd = -1;
        return -1;
    }
    
    if (listen(config->socket_fd, MAX_CONNECTIONS) < 0) {
        close(config->socket_fd);
        config->socket_fd = -1;
        return -1;
    }
    
    config->port = port;
    config->address = server_addr;
    
    return 0;
}

ssize_t network_send(int socket_fd, const void* data, size_t size) {
    if (socket_fd < 0 || !data || size == 0) {
        return -1;
    }
    
    return send(socket_fd, data, size, 0);
}

ssize_t network_receive(int socket_fd, void* buffer, size_t size) {
    if (socket_fd < 0 || !buffer || size == 0) {
        return -1;
    }
    
    return recv(socket_fd, buffer, size, 0);
}

NetworkStatus network_get_status(const NetworkConfig* config) {
    if (!config) {
        return NET_STATUS_ERROR;
    }
    
    if (config->socket_fd < 0) {
        return NET_STATUS_DISCONNECTED;
    }
    
    return NET_STATUS_CONNECTED;
}

const char* network_status_string(NetworkStatus status) {
    switch (status) {
        case NET_STATUS_DISCONNECTED: return "Disconnected";
        case NET_STATUS_CONNECTING: return "Connecting";
        case NET_STATUS_CONNECTED: return "Connected";
        case NET_STATUS_ERROR: return "Error";
        default: return "Unknown";
    }
}

int network_set_nonblocking(int socket_fd) {
    if (socket_fd < 0) {
        return -1;
    }
    
    int flags = fcntl(socket_fd, F_GETFL, 0);
    if (flags < 0) {
        return -1;
    }
    
    return fcntl(socket_fd, F_SETFL, flags | O_NONBLOCK);
}