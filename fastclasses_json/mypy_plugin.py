from mypy.plugin import Plugin, ClassDefContext
from mypy.plugins.common import add_method_to_class

from mypy.types import AnyType, TypeOfAny, CallableType
from mypy.typevars import fill_typevars
from mypy.nodes import (
    ARG_POS, MDEF, Argument, Var, FuncDef, Block, PassStmt, Decorator,
    SymbolTableNode
)
from mypy.semanal import set_callable_name
from mypy.util import get_unique_redefinition_name


class FastclassesJsonPlugin(Plugin):
    def get_class_decorator_hook(self, fullname: str):
        if fullname == "fastclasses_json.api.dataclass_json":
            return update_dataclass_json_type
        return None


def plugin(version: str):
    # ignore version argument if the plugin works with all mypy versions.
    return FastclassesJsonPlugin


def update_dataclass_json_type(ctx: ClassDefContext) -> None:

    str_type = ctx.api.named_type('__builtins__.str')
    # TODO: add arguments for separators and indent
    add_method_to_class(
        ctx.api, ctx.cls, 'to_json', args=[], return_type=str_type
    )

    # It would be lovely to actually have this return a typed dict ;)

    json_dict_type = ctx.api.named_type(
        '__builtins__.dict',
        [str_type, AnyType(TypeOfAny.explicit)]
    )
    add_method_to_class(
        ctx.api, ctx.cls, 'to_dict', args=[], return_type=json_dict_type
    )

    instance_type = fill_typevars(ctx.cls.info)
    arg = Argument(Var('o', json_dict_type), json_dict_type, None, ARG_POS)
    add_classmethod_to_class(
        ctx.api, ctx.cls, 'from_dict',
        args=[arg],
        return_type=instance_type,
    )

    # TODO: should be Union[str, bytes]
    arg = Argument(Var('json_data', str_type), str_type, None, ARG_POS)
    add_classmethod_to_class(
        ctx.api, ctx.cls, 'from_json',
        args=[arg],
        return_type=instance_type,
    )


def add_classmethod_to_class(
    api, cls, name, args, return_type, self_type=None, tvar_def=None
):
    """Adds a new classmethod to a class definition."""

    info = cls.info

    # First remove any previously generated methods with the same name
    # to avoid clashes and problems in the semantic analyzer.
    if name in info.names:
        sym = info.names[name]
        if sym.plugin_generated and isinstance(sym.node, Decorator):
            cls.defs.body.remove(sym.node)

    self_type = self_type or fill_typevars(info)
    class_type = api.class_type(self_type)

    function_type = api.named_type('__builtins__.function')

    args = [Argument(Var('cls'), class_type, None, ARG_POS)] + args
    arg_types, arg_names, arg_kinds = [], [], []
    for arg in args:
        assert arg.type_annotation, 'All arguments must be fully typed.'
        arg_types.append(arg.type_annotation)
        arg_names.append(arg.variable.name)
        arg_kinds.append(arg.kind)

    signature = CallableType(
        arg_types, arg_kinds, arg_names, return_type, function_type
    )
    if tvar_def:
        signature.variables = [tvar_def]

    func = FuncDef(name, args, Block([PassStmt()]))
    func.type = set_callable_name(signature, func)
    func._fullname = info.fullname + '.' + name
    func.line = info.line
    func.is_class = True

    var = Var(name)
    var.line = info.line
    var.info = info
    var.is_classmethod = True

    # should we have a NameExpr in the decorator list?
    dec = Decorator(func, [], var)
    dec.line = info.line

    # NOTE: we would like the plugin generated node to dominate, but we still
    # need to keep any existing definitions so they get semantically analyzed.
    if name in info.names:
        # Get a nice unique name instead.
        r_name = get_unique_redefinition_name(name, info.names)
        info.names[r_name] = info.names[name]

    info.names[name] = SymbolTableNode(MDEF, dec, plugin_generated=True)
    info.defn.defs.body.append(dec)
