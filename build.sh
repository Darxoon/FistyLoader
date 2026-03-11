#!/bin/bash

TYPE=steam_win

parse_args() {
    if ! options=$(getopt -o "t:ch" --long "type:,clean,help" -- "$@")
    then
        # Error, getopt will put out a message for us
        exit 1
    fi

    eval set -- $options
    
    while [ $# -gt 0 ]; do
        case $1 in
            -t|--type)
                TYPE=$2
                shift
            ;;
            -h|--help)
                # Inaccurate but i can't be bothered to write by hand
                python3 patcher/main.py --help
                exit 0
            ;;
        esac
        shift
    done
}

parse_args $@

set -e

# preprocess
python3 patcher/preprocess_hooks.py "$TYPE"

# assemble
ASMFLAGS="-f elf64"
if [ "$TYPE" == "steam_win" ]; then
    ASMFLAGS="$ASMFLAGS -dSTEAM"
fi

mkdir -p "ver/$TYPE/build/asm"
nasm patch/main.s $ASMFLAGS -o "ver/$TYPE/build/asm/main.o" &

# compile
CFLAGS="-c -I include -mabi=ms -O2 -fno-stack-protector -pedantic -pedantic-errors -Wall -Wextra"
if [ "$ENABLE_LOGGING" == 1 ]; then
    CFLAGS="$CFLAGS -D ENABLE_LOGGING"
fi

mkdir -p "ver/$TYPE/build/cpp"
gcc $CFLAGS -o "ver/$TYPE/build/cpp/ballTable.o" patch/src/ballTable.cpp &
gcc $CFLAGS -o "ver/$TYPE/build/cpp/ballFactory.o" patch/src/ballFactory.cpp &

# wait for assembly and compilataion to finish
# TODO: test for exit codes
wait

# link
OFILES="ver/$TYPE/build/asm/main.o ver/$TYPE/build/cpp/ballTable.o ver/$TYPE/build/cpp/ballFactory.o"
ld -o "ver/$TYPE/build/custom_code.o" --oformat elf64-x86-64 -T "ver/$TYPE/build/main.ld" $OFILES

# copy
objcopy "ver/$TYPE/build/custom_code.o" -O binary "ver/$TYPE/build/custom_code.bin"
objcopy "ver/$TYPE/build/custom_code.o" --only-keep-debug "ver/$TYPE/build/custom_code_symbols.o"

# build debug executable
[ "$1" != "--no-debug" ] && python3 patcher/main.py $@
