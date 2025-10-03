#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {

// InstructionCounter demonstrates a basic LLVM analysis pass
// This pass iterates over functions and counts instructions
// It could be expanded to:
// - Count specific instruction types (arithmetic, memory, branches)
// - Perform more complex analyses like dependency tracking
// - Integrate with optimization passes to guide transformations
// - Collect statistics for profiling or debugging

struct InstructionCounter : public FunctionPass {
    static char ID;
    InstructionCounter() : FunctionPass(ID) {}

    bool runOnFunction(Function &F) override {
        unsigned count = 0;
        for (auto &BB : F) {
            for (auto &I : BB) {
                count++;
                // Expansion idea: categorize by instruction type
                // if (isa<BinaryOperator>(&I)) arithCount++;
                // else if (isa<LoadInst>(&I)) loadCount++;
            }
        }
        errs() << "Function " << F.getName() << " has " << count << " instructions\n";
        return false; // Analysis pass, no modification
    }
};

}

char InstructionCounter::ID = 0;

// Register the pass for dynamic loading
// This allows using: opt -load ./libInstructionCounter.so -instcount input.bc
// Could be expanded to create pass pipelines or custom pass managers
static RegisterPass<InstructionCounter> X("instcount", "Count instructions in functions",
                                         false, // is analysis
                                         false); // doesn't modify CFG