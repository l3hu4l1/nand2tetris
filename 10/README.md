# compiler (i)
Translates Jack programs into VM bytecode. My implementation is split into a syntax analyzer and code generator.

The analyzer takes in Jack program(s) and outputs XML file(s) reflecting each program’s syntactic structure.
```
JackAnalyzer.py <path>
```

The algorithm used is recursive descent parsing:

<img src="Screenshot 2025-07-24 at 12.15.56 AM.png" width="70%">
