# operating system
My OS is a collection of Jack classes providing these services
- Math: basic mathematical operations;
- String: String type and string-related operations;
- Array: Array type and array-related operations;
- Output: screen output;
- Memory: memory operations;
- Sys: execution-related operations.

The executables are the compiled VM files. The Hack platform is programmed to first run the Sys.init function, which in turn runs the Main.main function. This function will then call various subroutines from both the user program and OS classes.

### Features
1. efficient multiplication, division, square root
2. dynamic memory allocation with defragging
3. variable-length arrays and strings
