# assembler
The Hack machine language consists of addressing instruction (A) and compute instruction (C):

<img src="Screenshot 2025-07-23 at 11.56.26 PM.png" width="60%">

The assembler takes in assembly commands and emits the corresponding instructions.
```
Assembler.py <filename>.asm | <directory>
```

Each command is translated separately. In particular, each mnemonic component is translated into its bit code and each symbol is resolved to its numeric address.

The resulting code can be loaded as is into the computer’s memory and executed.
