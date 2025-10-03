#include <stdio.h>

// This function will be compiled to LLVM IR.
// Our pass will target the addition operation inside it.
int simple_add(int a, int b) {
    return a + b;
}

int main() {
    int a = 10;
    int b = 5;
    // We will call the JIT-compiled version of simple_add from our C++ driver,
    // so this main function is primarily for generating the initial IR.
    printf("C main (for IR generation only): %d + %d = %d\n", a, b, simple_add(a, b));
    return 0;
}

