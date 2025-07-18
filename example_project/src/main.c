#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_NAME_LENGTH 100
#define DEBUG_MODE 1

typedef int UserID;
typedef char* UserName;
typedef struct User* UserPtr;

struct User {
    UserID id;
    UserName name;
    int age;
    float height;
    UserPtr next;
};

enum UserStatus {
    ACTIVE,
    INACTIVE,
    PENDING,
    DELETED
};

enum UserRole {
    ADMIN = 1,
    USER = 2,
    GUEST = 3
};

static int validate_user_id(UserID id) {
    return id > 0;
}

UserPtr create_user(UserName name, int age) {
    UserPtr user = malloc(sizeof(struct User));
    if (user) {
        user->name = strdup(name);
        user->age = age;
        user->next = NULL;
    }
    return user;
}

void destroy_user(UserPtr user) {
    if (user) {
        free(user->name);
        free(user);
    }
}

int get_user_age(UserPtr user) {
    return user ? user->age : -1;
}

UserID global_user_counter = 0;
UserPtr global_user_list = NULL;

int main() {
    UserPtr user = create_user("John Doe", 30);
    if (user) {
        printf("Created user: %s, age: %d\n", user->name, user->age);
        destroy_user(user);
    }
    return 0;
}