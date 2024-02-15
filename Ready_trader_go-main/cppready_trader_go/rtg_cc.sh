#!/bin/bash

rm autotrader

cmake -DCMAKE_BUILD_TYPE=Debug -B build

cmake --build build --config Debug

cp build/autotrader .

