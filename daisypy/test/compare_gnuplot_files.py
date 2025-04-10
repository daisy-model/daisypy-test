# pylint: disable=duplicate-code
'''Compare two dlf files using smallest meaningfull levels'''
from itertools import zip_longest

__all__ = [
    'compare_gnuplot_files'
]

default_lines_to_skip = frozenset(
    ()
)

DEFAULT_STRIP_TOKENS = None

def compare_gnuplot_files(path1,
                          path2,
                          skip_lines=default_lines_to_skip,
                          strip_tokens=DEFAULT_STRIP_TOKENS,
                          **_):
    '''Compare two gnuplot files

    Parameters
    ----------
    path1, path2 : str
      Paths to gnuplot files

    skip_lines: set of str
      Skip lines that begin with one of the strings in skip_lines

    strip_tokens: str
      Tokens to strip from strings before matching against skip_lines

    Returns
    -------
    (errors, not_similar, not_identical)
      errors: list of str
      not_similar: list of str
      not_identical: list of str
    '''
    errors = []
    not_identical = []
    not_similar = []
    keep = _drop_lines_starting_with(skip_lines, strip_tokens)
    try:
        with open(path1, encoding='locale') as file1, open(path2, encoding='locale') as file2:
            log1 = filter(keep, file1)
            log2 = filter(keep, file2)
            for line1, line2 in zip_longest(log1, log2):
                if line1 != line2:
                    not_similar.append(f'{line1} != {line2}')
    except OSError as e:
        errors.append(e)
    return errors, not_similar, not_identical

def _drop_lines_starting_with(drop_tokens, strip_tokens):
    def keep(s):
        s = s.strip(strip_tokens)
        return not any((s.startswith(token) for token in drop_tokens))
    return keep
