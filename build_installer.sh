# Creates PyInstaller executable of installer
# Make sure you have nasm installed

if [ ! -d '.venv' ]; then
    echo Python venv has not been created yet.
    echo Run this first and then try again: python -m venv .venv
    exit 1
fi

if [ -d '.venv/Scripts' ]; then
    source .venv/Scripts/activate
elif [ -d '.venv/bin' ]; then
    source .venv/bin/activate
else
    echo Invalid venv.
    exit 1
fi

pip install -r requirements.txt

if [ "$1" != "--no-compile" ]; then
    # build custom code & custom code symbols
    ./build.sh --no-debug --type steam_win
    ./build.sh --no-debug --type win
fi

# collect all version-specific files for all versions used by installer
PYI_DATA=
for VER_DIR in ver/*; do
    PYI_DATA="$PYI_DATA \
        --add-data $VER_DIR/hooks.yaml:$VER_DIR \
        --add-data $VER_DIR/build/custom_code.bin:$VER_DIR/build \
        --add-data $VER_DIR/build/custom_code_symbols.o:$VER_DIR/build"
done

pyinstaller -F patcher/install.py $PYI_DATA \
    --recursive-copy-metadata readchar --name FistyLoader_Install --clean

echo Done.
