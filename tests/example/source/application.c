#include "network.h"
#include "database.h"
#include "common.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>

static volatile int running = 1;

void signal_handler(int sig) {
    if (sig == SIGINT || sig == SIGTERM) {
        running = 0;
    }
}

int main(int argc, char* argv[]) {
    printf("Starting application...\n");
    
    // Setup signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Initialize network configuration
    NetworkConfig net_config;
    if (network_init(&net_config) < 0) {
        fprintf(stderr, "Failed to initialize network\n");
        return 1;
    }
    
    // Initialize database configuration
    DatabaseConfig db_config;
    memset(&db_config, 0, sizeof(db_config));
    db_config.type = DB_TYPE_SQLITE;
    strcpy(db_config.db_name, "application.db");
    
    // Connect to database
    if (database_connect(&db_config) < 0) {
        fprintf(stderr, "Failed to connect to database\n");
        network_cleanup(&net_config);
        return 1;
    }
    
    printf("Database connected\n");
    
    // Start network server
    if (network_listen(&net_config, 8080) < 0) {
        fprintf(stderr, "Failed to start network server\n");
        database_disconnect(&db_config);
        network_cleanup(&net_config);
        return 1;
    }
    
    printf("Network server listening on port 8080\n");
    
    // Main application loop
    while (running) {
        // Check database connection
        if (!database_is_connected(&db_config)) {
            fprintf(stderr, "Database connection lost\n");
            break;
        }
        
        // Check network status
        NetworkStatus status = network_get_status(&net_config);
        if (status == NET_STATUS_ERROR) {
            fprintf(stderr, "Network error\n");
            break;
        }
        
        // Simulate some work
        sleep(1);
    }
    
    printf("Shutting down application...\n");
    
    // Cleanup
    database_disconnect(&db_config);
    network_cleanup(&net_config);
    
    printf("Application stopped\n");
    return 0;
}