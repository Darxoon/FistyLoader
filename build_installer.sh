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
    ./build.sh --no-debug
fi

pyinstaller -F patcher/install.py --add-data patcher/custom_code.bin:. \
    --add-data patcher/custom_code_symbols.o:. --add-data patcher/data/hooks.yaml:data \
    --recursive-copy-metadata readchar --name FistyLoader_Install --clean

echo Done.
