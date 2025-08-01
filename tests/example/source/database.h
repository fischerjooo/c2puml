#ifndef DATABASE_H
#define DATABASE_H

#include <sqlite3.h>
#include <mysql/mysql.h>
#include <postgresql/libpq-fe.h>
#include <stdio.h>
#include <stdlib.h>
#include "common.h"

#define MAX_QUERY_LENGTH 4096
#define MAX_DB_NAME_LENGTH 256

typedef enum {
    DB_TYPE_SQLITE,
    DB_TYPE_MYSQL,
    DB_TYPE_POSTGRESQL
} DatabaseType;

typedef struct {
    DatabaseType type;
    char db_name[MAX_DB_NAME_LENGTH];
    char host[256];
    int port;
    char username[128];
    char password[128];
    void* connection;  // Type depends on database type
} DatabaseConfig;

typedef struct {
    int row_count;
    int column_count;
    char** data;
    char** column_names;
} QueryResult;

// Database connection management
int database_connect(DatabaseConfig* config);
void database_disconnect(DatabaseConfig* config);
int database_is_connected(const DatabaseConfig* config);

// Query execution
QueryResult* database_execute_query(DatabaseConfig* config, const char* query);
int database_execute_update(DatabaseConfig* config, const char* query);
void database_free_result(QueryResult* result);

// Transaction management
int database_begin_transaction(DatabaseConfig* config);
int database_commit_transaction(DatabaseConfig* config);
int database_rollback_transaction(DatabaseConfig* config);

// Utility functions
const char* database_get_error(const DatabaseConfig* config);
int database_escape_string(const DatabaseConfig* config, const char* input, char* output, size_t max_output_size);

#endif // DATABASE_H