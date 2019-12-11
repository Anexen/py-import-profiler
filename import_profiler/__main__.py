import os
import sys
import logging
import argparse

from import_profiler import install_hooks

logger = logging.getLogger("import_profiler")


class TreeFormatter(logging.Formatter):
    def formatMessage(self, record):
        level_mark = " | " * (record.depth - 1) if record.depth > 1 else ""
        direction_mark = " > " if record.event == "enter" else " < "
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

raw_header = "start, duration, mem, mem+, depth, event, module_name\n"

raw_formatter = logging.Formatter(
    "{start}, {duration}, "
    "{total_memory}, {memory_increase}, "
    "{depth}, {event}, {module_name}",
    style="{",
)

tree_header = "{:<10} {:<10} {:<7} {:<6}  {}\n".format(
    "start", "duration", "mem", "mem+", "module_name"
)

tree_formatter = TreeFormatter(
    "{start:<10.7f} {duration:<10.7f} "
    "{total_memory:<7} {memory_increase:<6} {module_name}",
    style="{",
)


def parse_args():
    parser = argparse.ArgumentParser(
        usage="python -m import_profiler [options] [scriptfile] [arg] ..."
    )
    parser.add_argument("-l", "--max-level")
    parser.add_argument("-L", "--max-library-level", default=1)
    parser.add_argument("-d", "--max-depth")
    parser.add_argument(
        "--full",
        action="store_true",
        default=False,
        help="ignore --max-level, --max-library-level, --depth settings",
    )

    out_group = parser.add_mutually_exclusive_group()
    out_group.add_argument(
        "-E",
        "--print-to-stderr",
        action="store_true",
        default=False,
        help="print to stderr instead of file",
    )
    out_group.add_argument(
        "-o", "--output", default="importtime.log", help="output file name"
    )

    display_group = parser.add_mutually_exclusive_group()
    display_group.add_argument(
        "--tree",
        action="store_true",
        default=True,
        help="show dependency tree",
    )
    display_group.add_argument(
        "--raw",
        action="store_true",
        default=False,
        help="export stats in csv format",
    )

    parser.add_argument("exec_args", nargs=argparse.REMAINDER)

    if not sys.argv[1:]:
        parser.print_usage()
        sys.exit(2)

    args = parser.parse_args()

    if not args.exec_args:
        parser.print_usage()
        sys.exit(2)

    return args


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

    if options.raw:
        handler.setFormatter(raw_formatter)
        handler.stream.write(raw_header)
    else:
        handler.setFormatter(tree_formatter)
        handler.stream.write(tree_header)

    if not options.full and options.max_depth:
        logger.addFilter(MaxDepthFilter(options.max_depth))

    if not options.full and options.max_level:
        logger.addFilter(MaxLevelFilter(options.max_level))

    if not options.full and options.max_library_level:
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
    args = parse_args()
    setup_logging(args)
    install_hooks()
    exec_script(args.exec_args)
