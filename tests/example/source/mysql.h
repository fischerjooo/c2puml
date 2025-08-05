#ifndef MYSQL_H
#define MYSQL_H

#include <stddef.h>

// Mock MySQL types
typedef struct st_mysql MYSQL;
typedef struct st_mysql_res MYSQL_RES;
typedef struct st_mysql_row MYSQL_ROW;
typedef struct st_mysql_field MYSQL_FIELD;

// Mock MySQL constants
#define MYSQL_SUCCESS 0
#define MYSQL_ERROR -1

// Mock MySQL function declarations
MYSQL* mysql_init(MYSQL* mysql);
MYSQL* mysql_real_connect(MYSQL* mysql, const char* host, const char* user, 
                      const char* passwd, const char* db, unsigned int port, 
                      const char* unix_socket, unsigned long clientflag);
void mysql_close(MYSQL* mysql);
int mysql_query(MYSQL* mysql, const char* query);
MYSQL_RES* mysql_store_result(MYSQL* mysql);
MYSQL_ROW mysql_fetch_row(MYSQL_RES* result);
void mysql_free_result(MYSQL_RES* result);
const char* mysql_error(MYSQL* mysql);
int mysql_ping(MYSQL* mysql);
unsigned int mysql_num_fields(MYSQL_RES* result);
unsigned long mysql_num_rows(MYSQL_RES* result);

#endif // MYSQL_H