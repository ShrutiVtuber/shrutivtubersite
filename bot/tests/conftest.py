# SPDX-License-Identifier: AGPL-3.0-only
"""
Shared test helpers.

`code_of` exists because the same mistake has now been made four times in this
project: a test greps a module for a forbidden string, and the module's own
comment — explaining *why* that thing is forbidden — is what matches. The
better a file documents its reasoning, the more likely it is to fail its own
check, which is precisely backwards.

So: strip the prose, search the code.
"""
from __future__ import annotations

import ast
import inspect
import re
from types import FunctionType, ModuleType


def code_of(target: ModuleType | FunctionType) -> str:
    """
    A module or function's source with docstrings and comments removed.

    Use this for any assertion of the form "this must not mention X". Searching
    raw source means a file cannot explain a decision without violating it.
    """
    source = inspect.getsource(target)
    if isinstance(target, FunctionType):
        source = re.sub(r"^\s+", "", source.split("\n")[0]) + "\n" + \
                 "\n".join(source.split("\n")[1:])
        source = inspect.cleandoc(inspect.getsource(target))

    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and ast.get_docstring(node):
            node.body = node.body[1:]
    # ast.unparse drops comments entirely, which is the other half of the job.
    return ast.unparse(tree)
