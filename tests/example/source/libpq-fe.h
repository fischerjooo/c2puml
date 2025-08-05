#ifndef LIBPQ_FE_H
#define LIBPQ_FE_H

#include <stddef.h>

// Mock PostgreSQL types
typedef struct pg_conn PGconn;
typedef struct pg_result PGresult;
typedef struct pg_stmt PGstmt;

// Mock PostgreSQL constants
#define CONNECTION_OK 0
#define CONNECTION_BAD 1

// Mock PostgreSQL types
typedef enum {
    PGRES_EMPTY_QUERY = 0,
    PGRES_COMMAND_OK = 1,
    PGRES_TUPLES_OK = 2,
    PGRES_COPY_OUT = 3,
    PGRES_COPY_IN = 4,
    PGRES_BAD_RESPONSE = 5,
    PGRES_NONFATAL_ERROR = 6,
    PGRES_FATAL_ERROR = 7
} ExecStatusType;

// Mock PostgreSQL function declarations
PGconn* PQconnectdb(const char* conninfo);
void PQfinish(PGconn* conn);
int PQstatus(const PGconn* conn);
PGresult* PQexec(PGconn* conn, const char* command);
int PQresultStatus(const PGresult* res);
int PQntuples(const PGresult* res);
int PQnfields(const PGresult* res);
char* PQgetvalue(const PGresult* res, int tup_num, int field_num);
char* PQfname(const PGresult* res, int field_num);
void PQclear(PGresult* res);
const char* PQerrorMessage(const PGconn* conn);

#endif // LIBPQ_FE_H