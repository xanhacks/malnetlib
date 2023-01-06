import dnlib
from dnlib.DotNet import *

class Attribute:

    def __init__(self, parent_object, core):
        self.object = parent_object
        self.core = core
        self._setup()

    def __str__(self):
        return f"{'public' if self.public else 'private'} " + \
            f"{'static' if self.static else ''} "\
            f"{self.type} {self.name} = {self.get_value()};"

    def __repr__(self):
        return f"<attribute {self.type} {self.name}>"

    def _setup(self):
        # TODO const/final ?
        self.name = self.core.get_Name().get_String()
        self.public = self.core.IsPublic
        self.static = self.core.IsStatic
        self.type = self.core.FieldType.TypeName
    
    def get_value(self):
        if self.core.HasConstant:
            return self.core.Constant.get_Value()
        elif self.static:
            cctor = self.object.get_method(".cctor")
            instructions = cctor.core.Body.Instructions  # opcodes
            last_value = None

            for inst in instructions:
                if last_value is not None:
                    if inst.OpCode.Name == "stsfld" and inst.Operand.Name.get_String() == self.name:
                        return last_value
                if inst.OpCode.Name == "ldstr":
                    last_value = inst.Operand

        return None


class Method:

    def __init__(self, obj, core):
        self.object = obj
        self.core = core
        self._setup()

    def __str__(self):
        return f"{'public' if self.public else 'private'} " + \
            f"{'final' if self.final else ''} "\
            f"{'static' if self.static else ''} "\
            f"{'virtual' if self.virtual else ''} "\
            f"{self.name}"

    def __repr__(self):
        return f"<method {self.name}>"

    def _setup(self):
        # TODO parameters and return value
        self.name = self.core.get_Name().get_String()
        self.public = self.core.IsPublic
        self.final = self.core.IsFinal
        self.static = self.core.IsStatic
        # self.virtual = self.IsVirtual


class Object:

    def __init__(self, core):
        self.core = core
        self._setup()

    def _setup(self):
        self.name = self.core.get_Name().get_String()
        self.public = self.core.IsPublic
        self.abstract = self.core.IsAbstract
        self.namespace = self.core.get_Namespace().get_String()
        self.type = "unknown"

        if self.core.IsClass:
            self.type = "class"
        elif self.core.IsInterface:
            self.type = "interface"
        elif self.core.IsEnum:
            self.type = "enum" 

    def __str__(self):
        return f"{'public' if self.public else 'private'} {self.core} {self.name}"

    def __repr__(self):
        return f"<{self.type} {self.name}>"

    def get_methods(self):
        return [Method(self, method) for method in self.core.Methods]

    def get_method(self, name):
        for method in self.core.Methods:
            meth_model = Method(self, method)
            if meth_model.name == name:
                return meth_model
        return None

    def get_attributes(self):
        return [Attribute(self, attribute) for attribute in self.core.get_Fields()]
    
    def get_attribute(self, name):
        for attribute in self.core.get_Fields():
            attr_model = Attribute(self, attribute)
            if attr_model.name == name:
                return attr_model
        return None


class DotNetPE:
    
    def __init__(self, sample_path):
        self.module = dnlib.DotNet.ModuleDefMD.Load(sample_path)

    def get_objects(self):
        return [Object(obj) for obj in self.module.Types]

    def get_object(self, name):
        for obj in self.module.Types:
            obj_model = Object(obj)
            if obj_model.name == name:
                return obj_model
        return None

