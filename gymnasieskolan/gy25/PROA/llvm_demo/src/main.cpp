#include <iostream>
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/Module.h"
#include "llvm/IRReader/IRReader.h"
#include "llvm/Support/SourceMgr.h"
#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/ExecutionEngine/ExecutionEngine.h"
#include "llvm/ExecutionEngine/GenericValue.h"
#include "llvm/ExecutionEngine/JIT.h"
#include "llvm/Support/TargetSelect.h"

using namespace llvm;

// Forward declare the pass registration function from Add2Sub.cpp
extern "C" ::llvm::PassPluginLibraryInfo LLVM_ATTRIBUTE_WEAK llvmGetPassPluginInfo();

int main(int argc, char **argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <input.ll>" << std::endl;
        return 1;
    }

    // Parse the input LLVM IR file
    LLVMContext Context;
    SMDiagnostic Err;
    std::unique_ptr<Module> Mod = parseIRFile(argv[1], Err, Context);
    if (!Mod) {
        Err.print(argv[0], errs());
        return 1;
    }

    // Expansion Idea 3: Custom Language Frontend
    // Instead of parsing an IR file, this is where a real compiler's frontend
    // would run. You would have a parser (e.g., using Bison/Flex) and an AST
    // (Abstract Syntax Tree). You would then walk the AST to generate LLVM IR
    // programmatically using llvm::IRBuilder.

    // Create a FunctionPassManager and add our custom pass.
    FunctionPassManager FPM;
    PassBuilder PB;
    // This is the modern way to register a pass plugin
    PB.registerPipelineParsingCallback(
        [](StringRef Name, FunctionPassManager &FPM, ArrayRef<PassBuilder::PipelineElement>) {
            if (Name == "add2sub") {
                FPM.addPass(Add2Sub());
                return true;
            }
            return false;
        }
    );

    // Add the pass to the manager.
    FPM.addPass(Add2Sub());

    // Run the pass on every function in the module.
    for (Function &F : *Mod) {
        FPM.run(F);
    }

    // Expansion Idea 4: More Complex Pass Pipeline
    // A real compiler runs dozens of passes. You could add standard LLVM
    // optimization passes here, like mem2reg, instcombine, gvn, etc.
    // The PassManager can be configured to run a complex pipeline of passes.

    std::cout << "--- Transformed LLVM IR ---" << std::endl;
    Mod->print(outs(), nullptr);
    std::cout << "---------------------------" << std::endl;

    // Now, JIT compile and execute the transformed code.
    InitializeNativeTarget();
    ExecutionEngine *EE = EngineBuilder(std::move(Mod)).create();
    if (!EE) {
        std::cerr << "Failed to create ExecutionEngine!" << std::endl;
        return 1;
    }

    // Find the function we want to call.
    Function *Func = EE->FindFunctionNamed("simple_add");
    if (!Func) {
        std::cerr << "Could not find simple_add function!" << std::endl;
        return 1;
    }

    // Prepare arguments for the function call.
    std::vector<GenericValue> Args(2);
    Args[0].IntVal = APInt(32, 10);
    Args[1].IntVal = APInt(32, 5);

    // Execute the function.
    GenericValue Result = EE->runFunction(Func, Args);

    std::cout << "--- JIT Execution Result ---" << std::endl;
    std::cout << "JIT-compiled simple_add(10, 5) = " << Result.IntVal.getSExtValue() << std::endl;
    std::cout << "(Note: The original C code would return 15, but our pass changed it to 10 - 5)" << std::endl;
    std::cout << "---------------------------" << std::endl;

    // Expansion Idea 5: Ahead-of-Time (AOT) Compilation
    // Instead of JIT, you could use LLVM's backend to compile the transformed IR
    // into an object file for a specific target (x86, ARM, etc.). This involves
    // setting up a `TargetMachine` and running a different set of passes to
    // generate machine code.

    delete EE;
    return 0;
}
