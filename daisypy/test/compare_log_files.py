'''Compare two log files using smallest meaningfull levels'''
import math
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
                      abs_tol=1e-8,
                      rel_tol=1e-2, # This is set low, because we mostly have summary numbers
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

    abs_tol: float
      Consider two numbers x, y equal if abs(x-y) < abs_tol

    rel_tol: float
      Consider two numbers x, y equal if max(abs((x-y)/x), abs((x-y)/y)) < rel_tol

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
    diff = []
    keep = _drop_lines_starting_with(skip_lines, strip_tokens)
    try:
        with open(path1, encoding='locale') as file1, open(path2, encoding='locale') as file2:
            log1 = filter(keep, dropwhile(program_not_ready, file1))
            log2 = filter(keep, dropwhile(program_not_ready, file2))
            for line1, line2 in zip_longest(log1, log2, fillvalue=''):
                err, not_sim, not_id = _compare_lines(line1, line2, abs_tol, rel_tol)
                errors += err
                not_similar += not_sim
                not_identical += not_id
    except OSError as e:
        errors.append(e)
    return errors, not_similar, not_identical

def _compare_lines(line1, line2, abs_tol, rel_tol):
    line1 = line1.strip()
    line2 = line2.strip()
    errors = []
    not_identical = []
    not_similar = []
    good = True
    # If the lines are only - and = we ignore them
    if line1 != line2 and not all((c in {'-', '='} for c in line1 + line2)):
        not_identical.append(f'"{line1}" | "{line2}"')

        # Check the numbers
        num_pattern = re.compile(r'-?\d*\.?\d+(?:[eE][+-]?\d+)?')
        numbers1 = re.findall(num_pattern, line1)
        numbers2 = re.findall(num_pattern, line2)
        if len(numbers1) != len(numbers2):
            not_similar.append(f'"{line1}" | "{line2}"')
            good = False
        else:
            for n1, n2 in zip(numbers1, numbers2):
                x, y = float(n1), float(n2)
                d = x - y
                if abs(d) > abs_tol:
                    if x == 0 or y == 0 or max(abs(d/x), abs(d/y)) > rel_tol:
                        not_similar.append(f'"{x}" != "{y}" in\n\t{line1}\n\t{line2}')
                        good = False
        if good:
            # If the numbers are good, check the rest of the string
            # We remove all the numbers, replace consecutive whitespace with a single space and make
            # -nan into nan
            multi_space_pattern = re.compile(r"\s{2,}")
            neg_nan_pattern = "-nan"
            s1 = re.sub(num_pattern, '', line1).strip()
            s1 = re.sub(multi_space_pattern, " ", s1)
            s1 = re.sub(neg_nan_pattern, "nan", s1)
            s2 = re.sub(num_pattern, '', line2).strip()
            s2 = re.sub(multi_space_pattern, " ", s2)
            s2 = re.sub(neg_nan_pattern, "nan", s2)
            if s1 != s2:
                not_similar.append(f'"{s1}" | "{s2}"')
    return errors, not_similar, not_identical

def _drop_lines_starting_with(drop_tokens, strip_tokens):
    def keep(s):
        s = s.strip(strip_tokens)
        return not any((s.startswith(token) for token in drop_tokens))
    return keep
