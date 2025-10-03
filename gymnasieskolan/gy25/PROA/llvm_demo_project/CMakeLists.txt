cmake_minimum_required(VERSION 3.13)
project(LLVMPassDemo)

# Find the LLVM package.
# This requires that LLVM is installed in a way that CMake can find it.
# You might need to set -DLLVM_DIR=/path/to/llvm/cmake/llvm when running cmake.
find_package(LLVM REQUIRED CONFIG)

# Set compiler to C++14
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add LLVM include directories and definitions.
include_directories(${LLVM_INCLUDE_DIRS})
add_definitions(${LLVM_DEFINITIONS})

# For modern LLVM, you need to handle these flags.
if(NOT CMAKE_CXX_FLAGS MATCHES "-fno-rtti")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-rtti")
endif()

# Create a shared library for our pass.
add_library(Add2Sub MODULE src/Add2Sub.cpp)

# Define the main executable.
add_executable(llvm_pass_demo src/main.cpp)

# Link the executable against the necessary LLVM components.
# The specific components may vary depending on your LLVM version.
llvm_map_components_to_libnames(LLVM_LIBS
    core
    irreader
    passes
    support
    executionengine
    mcjit
    )

# Link the executable.
target_link_libraries(llvm_pass_demo PRIVATE ${LLVM_LIBS})

# Print the include directories for debugging purposes.
message(STATUS "LLVM include dirs: ${LLVM_INCLUDE_DIRS}")
message(STATUS "LLVM library dirs: ${LLVM_LIBRARY_DIRS}")

