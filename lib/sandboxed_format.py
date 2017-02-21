"""
Based on
[Armin Robnacher's post](http://lucumr.pocoo.org/2016/12/29/careful-with-str-format/)
about not exposing internals by letting users access `str().format()`
"""
from string import Formatter
from collections import Mapping


class MagicFormatMapping(Mapping):
    """This class implements a dummy wrapper to fix a bug in the Python
    standard library for string formatting.

    See http://bugs.python.org/issue13598 for information about why
    this is necessary.
    """

    def __init__(self, args, kwargs):
        self._args = args
        self._kwargs = kwargs
        self._last_index = 0

    def __getitem__(self, key):
        if key == '':
            idx = self._last_index
            self._last_index += 1
            try:
                return self._args[idx]
            except LookupError:
                pass
            key = str(idx)
        return self._kwargs[key]

    def __iter__(self):
        return iter(self._kwargs)

    def __len__(self):
        return len(self._kwargs)

# This is a necessary API but it's undocumented and moved around
# between Python releases
try:
    from _string import formatter_field_name_split
except ImportError:
    formatter_field_name_split = lambda \
        x: x._formatter_field_name_split()


class SafeFormatter(Formatter):

    def get_field(self, field_name, args, kwargs):
        first, rest = formatter_field_name_split(field_name)
        obj = self.get_value(first, args, kwargs)
        for is_attr, i in rest:
            if is_attr:
                obj = safe_getattr(obj, i)
            else:
                obj = obj[i]
        return obj, first

# based on [`inspect` docs](https://docs.python.org/3/library/inspect.html)
UNSAFE_ATTRS = [
    'tb_frame',
    'tb_lasti',
    'tb_lineno',
    'tb_next',
    'f_back',
    'f_builtins',
    'f_code',
    'f_globals',
    'f_lasti',
    'f_lineno',
    'f_locals',
    'f_restricted',
    'f_trace',
    'co_argcount',
    'co_code',
    'co_consts',
    'co_filename',
    'co_firstlineno',
    'co_flags',
    'co_lnotab',
    'co_name',
    'co_names',
    'co_nlocals',
    'co_stacksize',
    'co_varnames',
    'gi_frame',
    'gi_running',
    'gi_code',
    'gi_yieldfrom',
    'cr_await',
    'cr_frame',
    'cr_running',
    'cr_code',
]


def safe_getattr(obj, attr):
    # Expand the logic here.  For instance on 2.x you will also need
    # to disallow func_globals, on 3.x you will also need to hide
    # things like cr_frame and others.  So ideally have a list of
    # objects that are entirely unsafe to access.
    if attr[:1] == '_' or attr in UNSAFE_ATTRS:
        raise AttributeError(attr)
    return getattr(obj, attr)


def safe_format(_string, *args, **kwargs):
    formatter = SafeFormatter()
    kwargs = MagicFormatMapping(args, kwargs)
    return formatter.vformat(_string, args, kwargs)
