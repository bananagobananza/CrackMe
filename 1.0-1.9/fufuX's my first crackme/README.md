# CrackMe Solution
LINK: https://crackmes.one/crackme/60c50c5d33c5d410b8842da6

## Description

This is my first crackme. It's probably one of the simplest C++ password systems. Don't patch it; just find the password.

## Solution

(Describe your solution here. You can use code blocks, lists, and other Markdown elements to make it clear and structured.)

### Steps to Solve

1. **Analyze the Binary:**
   - Use a disassembler like IDA Pro or Ghidra to inspect the binary.
   - Identify the function that handles password checking.

2. **Understand the Logic:**
   - Trace the password verification logic.
   - Look for comparison instructions that check the input against the correct password.

3. **Extract the Password:**
   - Find the hardcoded password or deduce it from the code.
   - Alternatively, use a debugger to step through the code and capture the correct password.

### Tools Used

- IDA Pro
- Ghidra
- GDB (GNU Debugger)
- (Any other tools you used)

### Detailed Walkthrough

(Provide a step-by-step walkthrough of your solution here. Use code blocks for any relevant code or assembly instructions.)

```cpp
// Example C++ code snippet
#include <iostream>
#include <string>

int main() {
    std::string password;
    std::cout << "Enter password: ";
    std::cin >> password;

    if (password == "correct_password") {
        std::cout << "Access granted!" << std::endl;
    } else {
        std::cout << "Access denied!" << std::endl;
    }

    return 0;
}
