#pragma once

#ifdef ENABLE_LOGGING

#include "wog2/environment.h"

extern Storage* printStorage;
extern FileHandle printHandle;

inline void initPrint(Storage* storage, FileHandle handle) {
    printStorage = storage;
    printHandle = handle;
}

// TODO: rewrite this as a C vararg
template<typename... Ts>
void printImpl(const char* fmt, Ts... args) {
    char buffer[0x80];
    int size = snprintf(buffer, sizeof(buffer), fmt, args...);
    printStorage->FileWrite(printHandle, buffer, size);
    printStorage->FileFlush(printHandle);
}

#define PRINT(...) printImpl(__VA_ARGS__)

#else

#define PRINT(...)

#endif
