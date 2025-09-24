"""
Utility functions for interacting with GDB via MI (Machine Interface).
See https://sourceware.org/gdb/current/onlinedocs/gdb#GDB_002fMI
"""

import importlib
import pkgutil

__all__ = []


# 遍历 utils 目录下的所有子模块
for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
    module = importlib.import_module(f".{module_name}", package=__name__)
    # 将模块中所有不以下划线开头的符号加入当前命名空间
    for name in getattr(module, "__all__", dir(module)):
        if not name.startswith("_"):
            globals()[name] = getattr(module, name)
            __all__.append(name)
