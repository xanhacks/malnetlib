import dnlib
from dnlib.DotNet import *
from dnlib.DotNet.Emit import *


class Resource:
    """Represents a .NET resource."""

    def __init__(self, core):
        self.core = core
        self._setup()

    def __str__(self):
        return self.core.get_FullName()

    def __repr__(self):
        return f"<Resource {self.name} 0x{self.offset}>"

    def _setup(self):
        self.name = self.core.get_Name().ToString()
        self.length = self.core.get_Length()
        self.offset = self.core.get_Offset()
        self.public = self.core.get_IsPublic()
        self.attributes = self.core.get_Attributes
        self.type = self.core.get_ResourceType()

    def read(self):
        """Return the content of the resource."""
        reader = self.core.CreateReader()
        data = reader.ReadBytes(self.length)
        return bytes(data)

    def save(self, filename):
        """Save the resource into an output file."""
        with open(filename, "wb") as output_file:
            output_file.write(self.read())


class Attribute:
    """Represents a .NET attribute."""

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
        """Return the value of the attribute."""
        if self.core.HasConstant:
            return self.core.Constant.get_Value()

        if self.static:
            cctor = self.object.get_method(".cctor")
            instructions = cctor.core.Body.Instructions  # opcodes
            last_value = None

            for inst in instructions:
                if last_value is not None:
                    if inst.OpCode == OpCodes.Stsfld and inst.Operand.Name.get_String() == self.name:
                        return last_value  # TODO: Transform "False" into False
                if inst.OpCode.Name == "ldstr":
                    last_value = inst.Operand

        return None


class Method:
    """Represents a .NET method."""

    def __init__(self, obj, core):
        self.object = obj
        self.core = core
        self._setup()

    def __str__(self):
        return self.core.get_FullName()

    def __repr__(self):
        return f"<method {self.name}>"

    def _setup(self):
        # TODO parameters type
        self.name = self.core.get_Name().get_String()
        self.public = self.core.IsPublic
        self.final = self.core.IsFinal
        self.static = self.core.IsStatic
        self.instructions = []
        if self.core.HasBody:
            self.instructions = self.core.Body.Instructions
        self.return_type = self.core.ReturnType.get_TypeName()
        self.has_params = self.core.get_HasParamDefs()
        self.params = []

        if self.has_params:
            for param in self.core.get_ParamDefs():
                self.params.append(param.name.get_String())

    def disassemble(self):
        """Disassemble a method."""
        for instr in self.instructions:
            print(instr)

class Object:
    """Represents a .NET object."""

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
        """Return all the .NET methods of the Object."""
        return [Method(self, method) for method in self.core.Methods]

    def get_method(self, name):
        """Return a .NET method based on his name inside the Object."""
        for method in self.core.Methods:
            meth_model = Method(self, method)
            if meth_model.name == name:
                return meth_model
        return None

    def get_attributes(self):
        """Return all the .NET attributes of the Object."""
        return [Attribute(self, attribute) for attribute in self.core.get_Fields()]

    def get_attribute(self, name):
        """Return an .NET attribute based on his name inside the Object."""
        for attribute in self.core.get_Fields():
            attr_model = Attribute(self, attribute)
            if attr_model.name == name:
                return attr_model
        return None


class DotNetPE:
    """Represents a PE written in .NET."""

    def __init__(self, sample_path):
        self.mod = dnlib.DotNet.ModuleDefMD.Load(sample_path)
        self.types = self.mod.Types
        self.resources = self.mod.Resources

    def patch_check_debugger(self):
        """
        Invert jump after a call to Debugger::get_IsAttached()

        IL_0000: call System.Boolean System.Diagnostics.Debugger::get_IsAttached()
        IL_0005: brfalse IL_0015
        IL_000A: ldstr "Debugger Detected"
        IL_000F: newobj System.Void System.Exception::.ctor(System.String)
        IL_0014: throw
        IL_0015: ret
        """
        found = False
        for method, instr in self.instructions_iterator():
            if found and instr.OpCode in [OpCodes.Brfalse, OpCodes.Brtrue]:
                found = False
                instr.OpCode = OpCodes.Brfalse if instr.OpCode == OpCodes.Brtrue else OpCodes.Brtrue
            elif instr.OpCode == OpCodes.Call and instr.Operand:
                if instr.Operand.get_FullName() == "System.Boolean System.Diagnostics.Debugger::get_IsAttached()":
                    found = True

    def save(self, filename):
        """Save PE file on disk."""
        self.mod.Write(filename)

    def get_objects(self):
        """Return all the .NET objects of the PE."""
        return [Object(obj_type) for obj_type in self.types]

    def get_object(self, name):
        """Return an .NET object based on his name."""
        for obj_type in self.types:
            obj_model = Object(obj_type)
            if obj_model.name == name:
                return obj_model
        return None

    def get_resources(self):
        """Return all the .NET resources of the PE."""
        return [Resource(res_type) for res_type in self.resources]

    def instructions_iterator(self):
        """Return an iterator that loop over all the instructions of the PE."""
        for obj_type in self.types:
            for method_type in obj_type.Methods:
                method = Method(obj_type, method_type)
                for instr in method.instructions:
                    yield method, instr

    def dump_strings(self):
        """Dump all strings of the PE."""
        return [instr.Operand for _, instr in self.instructions_iterator() \
                if instr.OpCode == OpCodes.Ldstr]

