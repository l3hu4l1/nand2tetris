# virtual machine
Translates VM code into assembly code conforming to the Hack platform. It is modeled after Java Virtual Machine's (JVM) architecture.
```
VMTranslator.py <filename>.vm | <directory>
```

The VM utilises four types of commands: arithmetic, memory access, program flow, and subroutine calling. A stack is used to handle all the associated operations.

<img src="Screenshot 2025-07-24 at 12.03.01 AM.png" width="60%">

The translated code emulates the memory segments of each VM function and file, as well as the implicit stack.
