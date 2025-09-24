'''Compare two log files using smallest meaningfull levels'''
import re
from itertools import zip_longest, dropwhile

__all__ = [
    'compare_log_files'
]

default_lines_to_skip = frozenset(
    (
        'Changing',
        'Command line',
        'Copyright',
        'Daisy',
        'Executable',
        'Has DAISYHOME',
        'In directory',
        'Interpreting',
        'Opening',
        'Parsing',
        'Program',
        'Reseting',
        'Spawning',
        'Storing',
        'Time',
        'Trying',
        'Using',
    )
)

DEFAULT_STRIP_TOKENS = ' \t\n*'

# pylint: disable=too-many-locals ; I don't think code gets clearer by rewriting with fewer locals
def compare_log_files(path1, path2,
                      skip_lines=default_lines_to_skip,
                      strip_tokens=DEFAULT_STRIP_TOKENS,
                      precision=1e-8,
                      **_):
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
      Consider two numbers equal if their absolute difference is less than this value.

    Returns
    -------
    (errors, not_similar, not_identical)
      errors: list of str
      not_similar: list of str
      not_identical: list of str
    '''
    def program_not_ready(s):
        return not s.startswith("Storing 'daisy.log'")

    errors = []
    not_identical = []
    not_similar = []
    keep = _drop_lines_starting_with(skip_lines, strip_tokens)
    try:
        with open(path1, encoding='locale') as file1, open(path2, encoding='locale') as file2:
            log1 = filter(keep, dropwhile(program_not_ready, file1))
            log2 = filter(keep, dropwhile(program_not_ready, file2))
            for line1, line2 in zip_longest(log1, log2, fillvalue=''):
                if line1 != line2 and not _compare_equations(line1, line2, precision):
                    not_similar.append(f'{line1} != {line2}')
    except OSError as e:
        errors.append(e)
    return errors, not_similar, not_identical

def _drop_lines_starting_with(drop_tokens, strip_tokens):
    def keep(s):
        s = s.strip(strip_tokens)
        return not any((s.startswith(token) for token in drop_tokens))
    return keep

def _compare_equations(line1, line2, precision):
    equation_pattern = re.compile(
        r'(?P<var>[\S]+)[\s]+=[\s]+(?P<value>[\S]+)[\s]+(?P<unit>[\S]+)[\s]+(?P<comment>[\S]+)'
    )
    eq1 = equation_pattern.match(line1)
    eq2 = equation_pattern.match(line2)
    if eq1 is None or eq2 is None:
        return False
    if ((eq1.group('var') != eq2.group('var')) or
        (eq1.group('unit') != eq2.group('unit')) or
        (eq1.group('comment') != eq2.group('comment'))):
        return False
    try:
        if abs(float(eq1.group('value')) - float(eq2.group('value'))) > precision:
            return False
    except TypeError:
        return False
    return True
