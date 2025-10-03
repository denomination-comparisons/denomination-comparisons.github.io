# Simple LLVM Pass Demo

This project demonstrates a minimal, end-to-end workflow using the LLVM compiler infrastructure.

## Core Concepts Demonstrated

1.  **LLVM IR Generation**: A simple C file (`src/simple_lang.c`) is used as the source language. We use Clang to compile it into LLVM IR (`input.ll`).

2.  **Custom Pass**: A custom `FunctionPass` (`src/Add2Sub.cpp`) is implemented. This pass traverses the functions in a module and replaces every integer `add` instruction with a `sub` instruction.

3.  **Driver Application**: The main application (`src/main.cpp`) acts as the compiler driver. It loads the LLVM IR from the file, registers and runs the custom pass on it, and prints the modified IR.

4.  **JIT Compilation**: After modification, the driver uses LLVM's JIT compiler to execute the transformed code directly in memory and prints the result to show the functional change.

## Project Structure

```
llvm_demo/
├── src/
│   ├── main.cpp           # Main driver: loads IR, runs pass, JITs code.
│   ├── Add2Sub.cpp        # The custom `add` to `sub` optimization pass.
│   └── simple_lang.c      # A simple C file to generate initial LLVM IR.
├── CMakeLists.txt         # The build script for the project.
└── README.md              # This file.
```

## How to Build and Run

**Prerequisites**: `llvm`, `clang`, `cmake`

1.  **Generate LLVM IR from the C source**:
    ```sh
    clang -S -emit-llvm src/simple_lang.c -o input.ll
    ```

2.  **Build the project**:
    ```sh
    mkdir build
    cd build
    cmake ..
    make
    ```

3.  **Run the driver with the generated IR**:
    ```sh
    ./llvm_pass_demo ../input.ll
    ```
