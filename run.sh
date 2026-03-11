#!/bin/bash
./build.sh "$1" || exit $?

if [ "$WOG2_PATH" == "" ]; then
    echo 'Please set the environment variable $WOG2_PATH'
    exit 1
fi

# Create backup
[ -f "$WOG2_PATH/WorldOfGoo2_backup.exe" ] || cp "$WOG2_PATH/WorldOfGoo2.exe" "$WOG2_PATH/WorldOfGoo2_backup.exe"

cp out.exe "$WOG2_PATH/WorldOfGoo2.exe"
echo "Launching World of Goo 2..."
"$WOG2_PATH/WorldOfGoo2.exe"
