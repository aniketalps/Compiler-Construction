*Name: Aniket Kumar Lata

*Description:
This repository contains Python code for a Python to x86 compiler for a subset of Python which we call P0.

The compiler consists of various phases like flatenning to Python ASTs, parsing using Lex-Yacc and Register allocation.

P0 subset:
Add operator (+)
Unary subtract (-)
Integers
Input function (input())
Print function (print)

Input:
The main function in compile.py takes a valid P0 python program as input.

Output:
The code generates a .s assembly file. This file can be compiled in gcc to generate an executable on any x86 machine.
