'''Compare two txt files'''
from itertools import zip_longest, dropwhile

__all__ = [
    'compare_txt_files'
]

DEFAULT_STRIP_TOKENS = ' \t\n*'

def compare_txt_files(path1, path2, **_):
    '''Compare two Daisy log files

    Parameters
    ----------
    path1, path2 : str
      Paths to txt files

    Returns
    -------
    (errors, not_identical)
      errors: list of str
      not_similar: list of str
      not_identical: list of str
    '''
    errors = []
    not_identical = []
    not_similar = []
    try:
        with open(path1, encoding='locale') as file1, open(path2, encoding='locale') as file2:
            for line1, line2 in zip_longest(file1, file2):
                if line1 != line2:
                    not_similar.append(f'{line1} != {line2}')
    except OSError as e:
        errors.append(e)
    return errors, not_similar, not_identical