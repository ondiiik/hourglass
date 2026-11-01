#!/usr/bin/env bash
set -Eeuo pipefail


# Prepare build directory
CWD=$PWD
BUILD_ROOT="$PWD"
if [ "$(basename $BUILD_ROOT)" != ".out" ]
then
    BUILD_ROOT="$BUILD_ROOT/.out"
    mkdir -p "$BUILD_ROOT"
    cd "$BUILD_ROOT"
fi

if [ ${0:0:1} != "." ] && [ ${0:0:1} != "/" ]
then
    SRC_ROOT="$(dirname $(dirname $(realpath $CWD/$0)))"
else
    SRC_ROOT="$(dirname $(dirname $(realpath $0)))"
fi


# Download MicroPyhon sources
if [ ! -d "$BUILD_ROOT/micropython" ]
then
    git clone https://github.com/micropython/micropython.git -b v1.29.0
fi

# Install esp-idf
if [ ! -d "$BUILD_ROOT/esp-idf/xtensa-lx106-elf" ]
then
    mkdir "$BUILD_ROOT/esp-idf"
    cd "$BUILD_ROOT/esp-idf"
    wget https://micropython.org/resources/xtensa-lx106-elf-standalone.tar.gz
    zcat xtensa-lx106-elf-standalone.tar.gz | tar x
    rm xtensa-lx106-elf/bin/esptool.py
    cd "$BUILD_ROOT"
fi

export "PATH=$BUILD_ROOT/esp-idf/xtensa-lx106-elf/bin/:$PATH"


# Add hourglass sources to be bundled in
cp -fv ../main.py $BUILD_ROOT/micropython/ports/esp8266/modules/
cp -rvf ../drv $BUILD_ROOT/micropython/ports/esp8266/modules/
cp -rvf ../common $BUILD_ROOT/micropython/ports/esp8266/modules/
cp -rvf ../app $BUILD_ROOT/micropython/ports/esp8266/modules/


# Build MicroPython firmware
rm -rf "$BUILD_ROOT/micropython/ports/esp8266/build-ESP8266_GENERIC"
rm -f "$BUILD_ROOT/hourglass_esp8266.bin"
cd "$BUILD_ROOT/micropython"
make -C mpy-cross
cd "$BUILD_ROOT/micropython/ports/esp8266"
make submodules
make all
cp "$BUILD_ROOT/micropython/ports/esp8266/build-ESP8266_GENERIC/firmware.bin" "$BUILD_ROOT/hourglass_esp8266.bin"
