!#/bin/bash

./compile.py $1
file_name=$1
assembly=${file_name::(-2)}s
exe=${file_name::(-3)}
gcc -m32 *.c $assembly -o $exe -lm
./$exe
