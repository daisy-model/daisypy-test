'''Compare two log files using smallest meaningfull levels'''
import warnings
from itertools import zip_longest, dropwhile

from pint.errors import UndefinedUnitError, DimensionalityError

#pylint: disable=import-error, no-name-in-module
from daisypy.test.units import daisy_ureg, dlf_unit_to_pint_unit
from daisypy.test.sml import load_smallest_meaningful_level

__all__ = [
    'compare_log_files'
]

default_lines_to_skip = frozenset(
    (
        'Changing',
        'Command line',
        'Copyright',
        'Daisy',
        'Has DAISYHOME',
        'In directory',
        'Interpreting',
        'Opening',
        'Parsing',
        'Program',
        'Reseting',
        'Storing',
        'Trying',
        'Using',
    )
)

default_strip_tokens = ' \t\n*'

def compare_log_files(path1, path2,
                      skip_lines=default_lines_to_skip,
                      strip_tokens=default_strip_tokens,
                      precision=1e-8,
                      sml_identity_threshold=0.001):
    '''Compare two Daisy log files

    Parameters
    ----------
    path1, path2 : str
      Paths to log files

    skip_lines: set of str
      Skip lines that begin with one of the strings in skip_lines

    strip_tokens: str
      Tokens to strip from strings before matching against skip_lines

    precision: float
      Consider two numbers equal if their absolute difference is less than this value. Only used if
      no SML is available

    sml_identity_threshold: float
      Consider two values identical if their difference is less than sml_identity_threshold * sml

    Returns
    -------
    (errors, not_similar, not_identical) 
      errors: list of str
      not_similar: list of str
      not_identical: list of str
    '''
    def program_not_ready(s): return not s.startswith("Storing 'daisy.log'")
        
    errors = []
    not_identical = []
    not_similar = []
    keep = _drop_lines_starting_with(skip_lines, strip_tokens)
    try:
        with open(path1) as file1, open(path2) as file2:
            log1 = filter(keep, dropwhile(program_not_ready, file1))
            log2 = filter(keep, dropwhile(program_not_ready, file2))
            for line1, line2 in zip_longest(log1, log2):
                if line1 != line2:
                    not_similar.append(f'{line1} != {line2}')
    except Exception as e:
        errors.append(e)
    return errors, not_similar, not_identical

def _drop_lines_starting_with(drop_tokens, strip_tokens):
    def keep(s):
        s = s.strip(strip_tokens)
        return not any((s.startswith(token) for token in drop_tokens))
    return keep
