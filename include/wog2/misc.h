#pragma once

#include <cstddef>

template<typename T>
class PackedArray {
public:
    int count;
    int field_0x4;
    int field_0x8;
    int field_0xc;
    T values[32];
};

namespace std {
    class string {};
}

namespace FileSystemUtils {
    void CreateDir(const char* path);
}

extern "C" {
    extern const char* gooballIds[0x27];
    
    // i love having to define all C std functions i use myself
    int snprintf( char * s, size_t n, const char * format, ... );
    char* strncpy( char* dest, const char* src, size_t count );
    void* malloc( size_t size );
    void free( void *ptr );
    int set_errno( int error_value );
    int get_errno( int * pValue );
    long strtol( const char* str, char** str_end, int base );
    int isspace( int ch );
    
    bool SDL_ShowSimpleMessageBox(int flags, const char *title, const char *message, void *window);
};
