class SymbolTable:
    def __init__(self):
        self.class_scope = {}
        self.subroutine_scope = {}
        self.index_counters = {
            "STATIC": 0,
            "FIELD": 0,
            "ARG": 0,
            "VAR": 0
        }

    def startSubroutine(self):
        self.subroutine_scope.clear()
        self.index_counters["ARG"] = 0
        self.index_counters["VAR"] = 0

    def define(self, name, type_, kind):
        kind = kind.upper()
        index = self.index_counters[kind]

        entry = {
            "type": type_,
            "kind": kind,
            "index": index
        }

        if kind in {"STATIC", "FIELD"}:
            self.class_scope[name] = entry
        elif kind in {"ARG", "VAR"}:
            self.subroutine_scope[name] = entry
        else:
            raise ValueError(f"Invalid kind: {kind}")

        self.index_counters[kind] += 1

    def varCount(self, kind):
        kind = kind.upper()
        return self.index_counters.get(kind, 0)

    def kindOf(self, name):
        if name in self.subroutine_scope:
            return self.subroutine_scope[name]["kind"]
        if name in self.class_scope:
            return self.class_scope[name]["kind"]
        return None

    def typeOf(self, name):
        if name in self.subroutine_scope:
            return self.subroutine_scope[name]["type"]
        if name in self.class_scope:
            return self.class_scope[name]["type"]
        return None

    def indexOf(self, name):
        if name in self.subroutine_scope:
            return self.subroutine_scope[name]["index"]
        if name in self.class_scope:
            return self.class_scope[name]["index"]
        return None
