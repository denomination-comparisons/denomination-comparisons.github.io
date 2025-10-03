cmake_minimum_required(VERSION 3.10)
project(LLVMDemo)

find_package(LLVM REQUIRED CONFIG)

message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")

include_directories(${LLVM_INCLUDE_DIRS})
add_definitions(${LLVM_DEFINITIONS})

# Instruction Counter Pass - demonstrates writing a custom LLVM pass
# This could be expanded to other analysis passes like control flow analysis or data flow analysis
add_library(InstructionCounter MODULE InstructionCounter.cpp)

# Main demo program - shows how to load and run passes on LLVM IR
# This could be expanded to include optimization pipelines or code generation
add_executable(llvm-demo main.cpp)

llvm_map_components_to_libnames(llvm_libs support core irreader passes)
target_link_libraries(llvm-demo ${llvm_libs})