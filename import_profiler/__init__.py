import logging
import resource
import sys
import time
from importlib.machinery import (
    BYTECODE_SUFFIXES,
    EXTENSION_SUFFIXES,
    SOURCE_SUFFIXES,
    ExtensionFileLoader,
    FileFinder,
    SourceFileLoader,
    SourcelessFileLoader,
)


logger = logging.getLogger("import_profiler")


_ctx = {}


def _memory_usage():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def profile(exec_module_func):
    def inner(self, module):
        _ctx["depth"] += 1

        module_level = module.__name__.count(".") + 1

        memory_before = _memory_usage()
        start_time = time.time()

        logger.debug(
            "",
            extra={
                "time": start_time,
                "start": start_time - _ctx["start_time"],
                "duration": 0,
                "event": "enter",
                "depth": _ctx["depth"],
                "total_memory": memory_before,
                "memory_increase": 0,
                "module_name": module.__name__,
                "module_file": module.__file__,
                "module_level": module_level,
            },
        )

        exec_exception = None

        try:
            exec_module_func(self, module)
        except Exception as e:
            exec_exception = e

        memory_after = _memory_usage()
        end_time = time.time()

        logger.debug(
            "",
            extra={
                "time": end_time,
                "start": end_time - _ctx["start_time"],
                "duration": end_time - start_time,
                "event": "leave",
                "depth": _ctx["depth"],
                "total_memory": memory_after,
                "memory_increase": memory_after - memory_before,
                "module_name": (
                    "(error) " + module.__name__
                    if exec_exception
                    else module.__name__
                ),
                "module_file": module.__file__,
                "module_level": module_level,
            },
        )

        _ctx["depth"] -= 1

        if exec_exception:
            raise exec_exception

    return inner


def install_hooks():
    _ctx.update({"start_time": time.time(), "depth": 0})

    ExtensionFileLoader.exec_module = profile(ExtensionFileLoader.exec_module)
    SourceFileLoader.exec_module = profile(SourceFileLoader.exec_module)
    SourcelessFileLoader.exec_module = profile(
        SourcelessFileLoader.exec_module
    )
    sys.path_hooks.insert(
        0,
        FileFinder.path_hook(
            (ExtensionFileLoader, EXTENSION_SUFFIXES),
            (SourceFileLoader, SOURCE_SUFFIXES),
            (SourcelessFileLoader, BYTECODE_SUFFIXES),
        ),
    )
