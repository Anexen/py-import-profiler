Python import profiling
=============

Installation
------------

```
$ pip install git+https://github.com/Anexen/py-import-profiler
```

Usage
-----

```
$ python -m import_profiler script.py
```

Profiler writes logs into `importtime.log` file by default.

Available options
-----------------

```
$ python -m import_profiler --help
```

```
Usage: python -m import_profiler [options] [scriptfile] [arg] ...

Options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output=OUTPUT
                        output file name
  -l MAX_LEVEL, --max-level=MAX_LEVEL
  -L MAX_LIBRARY_LEVEL, --max-library-level=MAX_LIBRARY_LEVEL
  -d MAX_DEPTH, --max-depth=MAX_DEPTH
  -E, --print-to-stderr
                        print to stderr instead of file
  --tree                show dependency tree
  --raw                 export stats in csv format
  --full                ignore --max-level, --max-library-level, --depth
                        settings
```

`depth` - the number of packages in import path.
`level` - package level. `my.awasome.package` has level = 3.

Tree example
------------

Marks:

* `|` - depth
* `>` - module enter
* `<` - module exit


```
start      duration   mem     mem+    module_name
0.0091257  0.0000000  10856   0       > django
0.0108154  0.0000000  10856   0       |  > django.utils
0.0113778  0.0005624  10856   0       |  < django.utils
0.0115931  0.0000000  10856   0       |  > django.utils.version
0.0119581  0.0000000  10856   0       |  |  > datetime
0.0130267  0.0000000  11292   0       |  |  |  > math
0.0131114  0.0000846  11292   0       |  |  |  < math
0.0139077  0.0000000  11400   0       |  |  |  > _datetime
0.0139816  0.0000739  11400   0       |  |  |  < _datetime
0.0140870  0.0021288  11400   544     |  |  < datetime
0.0142605  0.0000000  11400   0       |  |  > subprocess
0.0146890  0.0000000  11400   0       |  |  |  > signal
0.0157940  0.0011051  11400   0       |  |  |  < signal
0.0161521  0.0000000  11612   0       |  |  |  > _posixsubprocess
0.0162218  0.0000696  11612   0       |  |  |  < _posixsubprocess
0.0164857  0.0000000  11640   0       |  |  |  > select
0.0165541  0.0000684  11640   0       |  |  |  < select
0.0167124  0.0000000  11640   0       |  |  |  > selectors
0.0177698  0.0010574  11640   0       |  |  |  < selectors
0.0179193  0.0036588  11640   240     |  |  < subprocess
0.0181422  0.0000000  11640   0       |  |  > distutils
0.0182765  0.0001342  11640   0       |  |  < distutils
0.0184615  0.0000000  11640   0       |  |  > distutils.version
0.0193326  0.0008712  11640   0       |  |  < distutils.version
0.0194337  0.0078406  11640   784     |  < django.utils.version
0.0195153  0.0103896  11640   784     < django
```

`django` package (depth = 1, level = 1) imports `django.utils` (depth = 2, level = 2)
and `django.utils.version` (depth = 2, level 3). `django.utils.version` imports
`datetime` (depth = 3, level = 1).
