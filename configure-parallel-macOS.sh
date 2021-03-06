#!/bin/bash

INSTALLPATH="$(dirname "$(echo "$(pwd)")")"
BUILDFOLDER="build-masterthesis-llvm-parallel-$(date +%Y_%m_%d_%H_%M_%S)"

export CC='/usr/local/opt/llvm/bin/clang'
export CFLAGS='-O3 -Wall'

export CXX='/usr/local/opt/llvm/bin/clang++'
export CXXFLAGS='-DNDEBUG -Wall -Wextra -Wno-unused -O3'

export LDFLAGS='-L/usr/local/opt/llvm/lib'
export CPPFLAGS='-I/usr/local/opt/llvm/include'

mkdir $BUILDFOLDER

./bootstrap.sh

cd $BUILDFOLDER

./../configure \
--enable-dist="no" \
--with-mpi='/usr/local/opt/openmpi' \
--enable-mpi="yes" \
--enable-openmp="yes" \
--with-boost='/usr/local/opt/boost@1.57' \
--with-boost-libdir='/usr/local/opt/boost@1.57/lib' \
--with-boost-serialization \
--enable-boost-mpi="yes" \
--with-netcdf='/usr/local/opt/netcdf' \
--with-hdf5='/usr/local/opt/hdf5/' \
--enable-netcdf="yes" \
--enable-adolc="no" \
--with-adolc='/usr/local/opt/adol-c' \
--enable-gmock="yes" \
--with-gmock='/usr/local/opt/gmock' \
--enable-doc="yes" \
--prefix="$INSTALLPATH/scafes-masterthesis-parallel-llvm"

make

exit 0
