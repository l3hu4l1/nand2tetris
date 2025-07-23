# compiler
The code generator manages a symbol table, representing and generating code for variables, objects, and arrays. It also translates control flow commands via post-order traversal of the underlying parse tree.

The following kinds of identifiers may appear in the table:

|Identifier| Scope |
| :---: | :---: |
| Static | class |
| Field | class |
| Argument | subroutine |
| Var | subroutine |

<img src="Screenshot 2025-07-24 at 12.21.34 AM.png" width="70%">

The compiler takes in Jack program(s) and outputs the corresponding VM program(s).

```JackCompiler.py <path>```
