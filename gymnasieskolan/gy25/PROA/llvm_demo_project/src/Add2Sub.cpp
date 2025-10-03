#include "llvm/IR/Function.h"
#include "llvm/Pass.h"
#include "llvm/IR/InstIterator.h"
#include "llvm/IR/Instructions.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {
struct Add2Sub : public FunctionPass {
    static char ID; 
    Add2Sub() : FunctionPass(ID) {}

    bool runOnFunction(Function &F) override {
        bool modified = false;
        // Iterate over all instructions in the function.
        for (inst_iterator I = inst_begin(F), E = inst_end(F); I != E; ++I) {
            Instruction *pInst = &*I;

            // Check if the instruction is a binary operator and if it's an 'add'.
            if (pInst->isBinaryOp() && pInst->getOpcode() == Instruction::Add) {
                // Create a new 'sub' instruction.
                Instruction *subInst = BinaryOperator::Create(
                    Instruction::Sub, 
                    pInst->getOperand(0), 
                    pInst->getOperand(1), 
                    "sub_result"
                );

                // Replace all uses of the old 'add' instruction with the new 'sub' instruction.
                pInst->replaceAllUsesWith(subInst);
                // The new instruction should be inserted right before the old one.
                subInst->insertBefore(pInst);

                // Mark the old instruction for deletion.
                // It's important to not delete it immediately while iterating.
                pInst->eraseFromParent();

                modified = true;

                // Expansion Idea 1: More Complex Analysis
                // Instead of blindly replacing, you could analyze the operands.
                // For example, only replace if one operand is a constant, or if the result
                // is used in a specific way (e.g., as a loop counter).

                // Expansion Idea 2: Configuration
                // This pass could be configured. For example, a command-line option could
                // tell it whether to replace adds with subs, muls, or divs, making it a
                // more general "BinaryOpSwapperPass".
            }
        }
        return modified;
    }
};
} // namespace

char Add2Sub::ID = 0;
static RegisterPass<Add2Sub> X("add2sub", "Add to Sub Pass",
                             false /* Only looks at CFG */,
                             false /* Is an analysis pass */);
