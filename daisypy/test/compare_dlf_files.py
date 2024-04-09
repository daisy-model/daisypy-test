'''Compare two dlf files using smallest meaningfull levels'''
import os
import warnings

from pint.errors import UndefinedUnitError, DimensionalityError

from daisypy.io.dlf import read_dlf
#pylint: disable=import-error, no-name-in-module
from daisypy.test.units import daisy_ureg, dlf_unit_to_pint_unit
from daisypy.test.sml import load_smallest_meaningful_level

__all__ = [
    'compare_dlf_files'
]

def compare_dlf_files(path1, path2,
                      skip_header=frozenset(('VERSION', 'RUN', 'SIMFILE')),
                      precision=1e-8,
                      sml_warn_level=0.001):
    '''Compare two dlf files

    Parameters
    ----------
    path1, path2 : str
      Paths to dlf files

    skip_header: set
      Header keys to exclude from comparison

    precision: float
      Consider two numbers equal if their absolute difference is less than this value

    sml_warn_level: float
      Emit a warning if the absolute difference between two numeric values is larger than this
      value times the corresponding sml

    Returns
    -------
    True if the files compare equal, False otherwise
    '''
    dlf1 = read_dlf(path1)
    dlf2 = read_dlf(path2)

    # Check headers match
    diff_headers = _compare_headers(dlf1.header, dlf2.header, skip_header)
    if len(diff_headers) > 0:
        return False

    diff_units = _compare_units(dlf1.units, dlf2.units)
    if len(diff_units) > 0:
        return False


    sml_names = [os.path.basename(path1), dlf1.header['dlf-component']]
    diff_bodies = _compare_bodies(dlf1.body,
                                  dlf2.body,
                                  dlf1.units,
                                  sml_names,
                                  precision,
                                  sml_warn_level)
    if len(diff_bodies) > 0:
        return False
    return True

def _compare_headers(h1, h2, skip_header):
    diff = []
    for k in (set(h1.keys()) | set(h2.keys())) - skip_header:
        if k not in h1:
            diff.append((k, None, h2[k]))
        elif k not in h2:
            diff.append((k, h1[k], None))
        elif h1[k] != h2[k]:
            diff.append((k, h1[k], h2[k]))
    return diff

def _compare_units(u1, u2):
    diff = []
    for k in set(u1.keys()) | set(u2.keys()):
        if k not in u1:
            diff.append((k, None, u2[k]))
        elif k not in u2:
            diff.append((k, u1[k], None))
        elif u1[k] != u2[k]:
            diff.append((k, u1[k], u2[k]))
    return diff

def _compare_bodies(b1, b2, units, sml_names, precision, sml_warn_level):
    # pylint: disable=too-many-arguments
    bad_diff = []
    try:
        diff = b1.compare(b2)
        if len(diff) > 0:
            sml_map = load_smallest_meaningful_level(sml_names, daisy_ureg)
            if len(sml_map) == 0:
                warnings.warn(f'No SML definitions loaded. Tried {sml_names}')
            for col in diff.columns.levels[0]:
                abs_delta = (diff[col]['self'] - diff[col]['other']).abs()
                max_abs_delta_idx = abs_delta.argmax()
                delta = abs_delta.iloc[max_abs_delta_idx]
                try:
                    sml = sml_map[col]
                    delta_u = (delta * dlf_unit_to_pint_unit(units[col], daisy_ureg)).to(sml)
                    if delta_u > sml:
                        bad_diff.append((col, b1[col].iloc[max_abs_delta_idx], b2[col].iloc[max_abs_delta_idx]))
                        print(f'ERROR: {delta_u} > {sml} for {col}')
                        print(diff[col].iloc[max_abs_delta_idx])
                    elif delta_u > sml_warn_level * sml:
                        warnings.warn(f'{delta_u} > {sml_warn_level * sml} for {col}')
                except KeyError:
                    # We dont have an SML
                    if delta > precision:
                        bad_diff.append((col, b1[col].iloc[max_abs_delta_idx], b2[col].iloc[max_abs_delta_idx]))
                        print(f'ERROR: {delta} > {precision} for {col}')
                        print(diff[col].iloc[max_abs_delta_idx])
                except UndefinedUnitError:
                    error = f'ERROR: Unknown unit {units[col]} for {col}'
                    print(error)
                    bad_diff.append((error, '', ''))
                except AttributeError:
                    error = f'ERROR: Unit conversion error {units[col]} for {col}'
                    print(error)
                    bad_diff.append((error, '', ''))
                except DimensionalityError:
                    error = f'ERROR: Unit mismatch {units[col]} !~ {sml_map[col]} for {col}'
                    print(error)
                    bad_diff.append((error, '', ''))
    except ValueError as e:
        bad_diff.append((e, '', ''))
    return bad_diff
