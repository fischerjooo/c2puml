#include "database.h"
#include <string.h>
#include <errno.h>

int database_connect(DatabaseConfig* config) {
    if (!config) {
        return -1;
    }
    
    switch (config->type) {
        case DB_TYPE_SQLITE: {
            sqlite3** db = (sqlite3**)&config->connection;
            int result = sqlite3_open(config->db_name, db);
            return (result == SQLITE_OK) ? 0 : -1;
        }
        case DB_TYPE_MYSQL: {
            MYSQL* mysql = mysql_init(NULL);
            if (!mysql) {
                return -1;
            }
            config->connection = mysql_real_connect(mysql, config->host, config->username, 
                                                  config->password, config->db_name, config->port, NULL, 0);
            return config->connection ? 0 : -1;
        }
        case DB_TYPE_POSTGRESQL: {
            char conn_string[1024];
            snprintf(conn_string, sizeof(conn_string), 
                    "host=%s port=%d dbname=%s user=%s password=%s",
                    config->host, config->port, config->db_name, 
                    config->username, config->password);
            
            PGconn* conn = PQconnectdb(conn_string);
            if (PQstatus(conn) != CONNECTION_OK) {
                PQfinish(conn);
                return -1;
            }
            config->connection = conn;
            return 0;
        }
        default:
            return -1;
    }
}

void database_disconnect(DatabaseConfig* config) {
    if (!config || !config->connection) {
        return;
    }
    
    switch (config->type) {
        case DB_TYPE_SQLITE:
            sqlite3_close((sqlite3*)config->connection);
            break;
        case DB_TYPE_MYSQL:
            mysql_close((MYSQL*)config->connection);
            break;
        case DB_TYPE_POSTGRESQL:
            PQfinish((PGconn*)config->connection);
            break;
    }
    
    config->connection = NULL;
}

int database_is_connected(const DatabaseConfig* config) {
    if (!config || !config->connection) {
        return 0;
    }
    
    switch (config->type) {
        case DB_TYPE_SQLITE:
            return 1;  // SQLite doesn't have connection status
        case DB_TYPE_MYSQL:
            return mysql_ping((MYSQL*)config->connection) == 0;
        case DB_TYPE_POSTGRESQL:
            return PQstatus((PGconn*)config->connection) == CONNECTION_OK;
        default:
            return 0;
    }
}

QueryResult* database_execute_query(DatabaseConfig* config, const char* query) {
    if (!config || !config->connection || !query) {
        return NULL;
    }
    
    QueryResult* result = malloc(sizeof(QueryResult));
    if (!result) {
        return NULL;
    }
    
    memset(result, 0, sizeof(QueryResult));
    
    switch (config->type) {
        case DB_TYPE_SQLITE: {
            sqlite3_stmt* stmt;
            if (sqlite3_prepare_v2((sqlite3*)config->connection, query, -1, &stmt, NULL) != SQLITE_OK) {
                free(result);
                return NULL;
            }
            
            result->column_count = sqlite3_column_count(stmt);
            // Simplified implementation - would need proper result handling
            sqlite3_finalize(stmt);
            break;
        }
        case DB_TYPE_MYSQL: {
            if (mysql_query((MYSQL*)config->connection, query) != 0) {
                free(result);
                return NULL;
            }
            
            MYSQL_RES* mysql_result = mysql_store_result((MYSQL*)config->connection);
            if (mysql_result) {
                result->column_count = mysql_num_fields(mysql_result);
                result->row_count = mysql_num_rows(mysql_result);
                mysql_free_result(mysql_result);
            }
            break;
        }
        case DB_TYPE_POSTGRESQL: {
            PGresult* pg_result = PQexec((PGconn*)config->connection, query);
            if (PQresultStatus(pg_result) != PGRES_TUPLES_OK) {
                PQclear(pg_result);
                free(result);
                return NULL;
            }
            
            result->column_count = PQnfields(pg_result);
            result->row_count = PQntuples(pg_result);
            PQclear(pg_result);
            break;
        }
        default:
            free(result);
            return NULL;
    }
    
    return result;
}

int database_execute_update(DatabaseConfig* config, const char* query) {
    if (!config || !config->connection || !query) {
        return -1;
    }
    
    switch (config->type) {
        case DB_TYPE_SQLITE: {
            char* error_msg = NULL;
            int result = sqlite3_exec((sqlite3*)config->connection, query, NULL, NULL, &error_msg);
            if (error_msg) {
                sqlite3_free(error_msg);
            }
            return (result == SQLITE_OK) ? 0 : -1;
        }
        case DB_TYPE_MYSQL:
            return mysql_query((MYSQL*)config->connection, query);
        case DB_TYPE_POSTGRESQL: {
            PGresult* result = PQexec((PGconn*)config->connection, query);
            ExecStatusType status = PQresultStatus(result);
            PQclear(result);
            return (status == PGRES_COMMAND_OK) ? 0 : -1;
        }
        default:
            return -1;
    }
}

void database_free_result(QueryResult* result) {
    if (!result) {
        return;
    }
    
    if (result->data) {
        for (int i = 0; i < result->row_count * result->column_count; i++) {
            free(result->data[i]);
        }
        free(result->data);
    }
    
    if (result->column_names) {
        for (int i = 0; i < result->column_count; i++) {
            free(result->column_names[i]);
        }
        free(result->column_names);
    }
    
    free(result);
}

int database_begin_transaction(DatabaseConfig* config) {
    return database_execute_update(config, "BEGIN");
}

int database_commit_transaction(DatabaseConfig* config) {
    return database_execute_update(config, "COMMIT");
}

int database_rollback_transaction(DatabaseConfig* config) {
    return database_execute_update(config, "ROLLBACK");
}

const char* database_get_error(const DatabaseConfig* config) {
    if (!config || !config->connection) {
        return "No connection";
    }
    
    switch (config->type) {
        case DB_TYPE_SQLITE:
            return sqlite3_errmsg((sqlite3*)config->connection);
        case DB_TYPE_MYSQL:
            return mysql_error((MYSQL*)config->connection);
        case DB_TYPE_POSTGRESQL:
            return PQerrorMessage((PGconn*)config->connection);
        default:
            return "Unknown database type";
    }
}