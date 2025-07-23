# operating system
My OS is a collection of Jack classes that provide these services:
- Math: basic mathematical operations;
- String: String type and string-related operations;
- Array: Array type and array-related operations;
- Output: screen output;
- Memory: memory operations;
- Sys: execution-related services.

It is itself written in Jack, so its executable version is the compiled VM files. The Hack platform is programmed to first run the Sys.init function, which in turn runs the Main.main function. This function will then call various subroutines from both the user program and OS classes.

**Features**
- efficient multiplication, division, square root
- dynamic memory allocation with defragging
- variable-length arrays and strings
