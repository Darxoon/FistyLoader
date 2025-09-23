#!/bin/bash
preprocess() {
    mkdir -p patch/build
    python3 patcher/preprocess_hooks.py
}

compile() {
    nasm patch/main.s -f elf64 -o patch/build/main.o &
    
    CFLAGS="-c -I include -mabi=ms -O2 -fno-stack-protector"
    if [ "$ENABLE_LOGGING" == 1 ]; then
        CFLAGS="$CFLAGS -D ENABLE_LOGGING"
    fi
    
    gcc $CFLAGS -o patch/build/ballTable.o patch/src/ballTable.cpp &
    gcc $CFLAGS -o patch/build/ballFactory.o patch/src/ballFactory.cpp &
    wait
}

link() {
    INPUT_FILES="patch/build/main.o patch/build/ballTable.o patch/build/ballFactory.o"
    ld -o patch/build/custom_code.o --oformat elf64-x86-64 -T main.ld $INPUT_FILES
}

copy() {
    objcopy patch/build/custom_code.o -O binary patcher/custom_code.bin
    objcopy patch/build/custom_code.o --only-keep-debug patcher/custom_code_symbols.o
}

preprocess && compile && link && copy && python3 patcher/main.py "$1"
