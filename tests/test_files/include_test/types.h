#ifndef TYPES_H
#define TYPES_H

#include <stddef.h>

typedef unsigned char Byte;
typedef unsigned short Word;
typedef unsigned long DWord;

typedef struct {
    Byte r, g, b, a;
} RGBA;

typedef struct {
    int width;
    int height;
    RGBA* pixels;
} Image;

typedef void (*ImageCallback)(Image* img);
typedef int (*CompareFunc)(const void*, const void*);

#define IMAGE_MAX_SIZE 4096
#define BYTES_PER_PIXEL 4

extern Byte default_alpha;
extern Word screen_width;
extern DWord memory_size;

#endif // TYPES_H