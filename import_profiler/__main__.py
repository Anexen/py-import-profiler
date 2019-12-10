import os
import sys
import logging
from optparse import OptionParser

from import_profiler import install_hooks

logger = logging.getLogger("import_profiler")


class TreeFormatter(logging.Formatter):
    def formatMessage(self, record):
        level_mark = " | " * (record.depth - 1) if record.depth > 1 else ""
        direction_mark = "> " if record.event == "enter" else "< "
        record.module_name = level_mark + direction_mark + record.module_name

        return super().formatMessage(record)


class MaxDepthFilter(logging.Filter):
    def __init__(self, max_depth):
        super().__init__()
        self.max_depth = max_depth

    def filter(self, record):
        return record.depth <= self.max_depth


class MaxLevelFilter(logging.Filter):
    def __init__(self, max_level):
        super().__init__()
        self.max_level = max_level

    def filter(self, record):
        return record.module_level <= self.max_level


class MaxLibraryLevelFilter(MaxLevelFilter):
    def filter(self, record):
        if "lib/python" not in record.module_file:
            return True

        return super().filter(record)


default_formatter = logging.Formatter("{message}", style="{")

raw_header = "start, duration, mem, mem+, depth, module_name\n"

raw_formatter = logging.Formatter(
    "{start}, {duration}, "
    "{total_memory}, {memory_increase}, "
    "{depth}, {module_name}",
    style="{",
)

tree_header = "{:<10} {:<10} {:<7} {:<6} {}\n".format(
    "start", "duration", "mem", "mem+", "module_name"
)

tree_formatter = TreeFormatter(
    "{start:<10.7f} {duration:<10.7f} "
    "{total_memory:<7} {memory_increase:<6} {module_name}",
    style="{",
)


def parse_args():
    parser = OptionParser(
        usage="python -m import_profiler [options] [scriptfile] [arg] ..."
    )
    parser.allow_interspersed_args = False

    parser.add_option(
        "-o", "--output", default="importtime.log", help="output file name"
    )
    parser.add_option("-l", "--max-level", default=None)
    parser.add_option("-L", "--max-library-level", default=1)
    parser.add_option("-d", "--max-depth", default=None)
    parser.add_option(
        "-E",
        "--print-to-stderr",
        action="store_true",
        default=False,
        help="print to stderr instead of file",
    )
    parser.add_option(
        "--tree",
        action="store_true",
        default=True,
        help="show dependency tree",
    )
    parser.add_option(
        "--raw",
        action="store_true",
        default=False,
        help="export stats in csv format",
    )
    parser.add_option(
        "--full",
        action="store_true",
        default=False,
        help="ignore --max-level, --max-library-level, --depth settings",
    )

    if not sys.argv[1:]:
        parser.print_usage()
        sys.exit(2)

    options, args = parser.parse_args()

    if not args:
        parser.print_usage()
        sys.exit(2)

    return options, args


def setup_logging(options):
    logger.setLevel(logging.DEBUG)

    if options.print_to_stderr:
        handler = logging.StreamHandler(stream=sys.stderr)
    else:
        # with mode='w' logger can lose first messages
        # https://stackoverflow.com/questions/39838616
        handler = logging.FileHandler(options.output)
        handler.stream.truncate(0)

    logger.addHandler(handler)

    handler.setFormatter(default_formatter)

    if options.tree:
        handler.setFormatter(tree_formatter)
        handler.stream.write(tree_header)
    else:
        handler.setFormatter(raw_formatter)
        handler.stream.write(raw_header)

    if not options.full and options.max_depth is not None:
        logger.addFilter(MaxDepthFilter(options.max_depth))

    if not options.full and options.max_level is not None:
        logger.addFilter(MaxLevelFilter(options.max_level))

    if not options.full and options.max_library_level is not None:
        logger.addFilter(MaxLibraryLevelFilter(options.max_library_level))


def exec_script(args):
    sys.argv[:] = args
    progname = args[0]

    sys.path.insert(0, os.path.dirname(progname))

    with open(progname, "rb") as fp:
        code = compile(fp.read(), progname, "exec")

    globs = {
        "__file__": progname,
        "__name__": "__main__",
        "__package__": None,
        "__cached__": None,
    }

    exec(code, globs, None)


if __name__ == "__main__":
    options, args = parse_args()
    setup_logging(options)
    install_hooks()
    exec_script(args)
