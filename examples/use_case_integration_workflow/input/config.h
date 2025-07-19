#ifndef CONFIG_H
#define CONFIG_H

#define CONFIG_VERSION "1.0.0"
#define DEFAULT_TIMEOUT 30

typedef struct {
    int id;
    char name[100];
} User;

enum Color {
    RED,
    GREEN,
    BLUE
};

void init_config(void);
int validate_config(void);

#endif