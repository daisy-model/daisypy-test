'''Compare two dlf files using smallest meaningfull levels'''
import warnings

from pint.errors import UndefinedUnitError, DimensionalityError

from daisypy.io.dlf import read_dlf
#pylint: disable=import-error, no-name-in-module
from daisypy.test.units import daisy_ureg, dlf_unit_to_pint_unit
from daisypy.test.sml import load_smallest_meaningful_level

__all__ = [
    'compare_dlf_files'
]

default_header_lines_to_skip = frozenset(
    ('VERSION', 'RUN', 'SIMFILE', 'SIM', 'dlf-def-location', 'info')
)

def compare_dlf_files(path1, path2,
                      skip_header=default_header_lines_to_skip,
                      precision=1e-8,
                      sml_identity_threshold=0.001):
    '''Compare two dlf files

    Parameters
    ----------
    path1, path2 : str
      Paths to dlf files

    skip_header: set
      Header keys to exclude from comparison

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
    dlf1 = read_dlf(path1)
    dlf2 = read_dlf(path2)

    diff_headers = _compare_headers(dlf1.header, dlf2.header, skip_header)
    if len(diff_headers) > 0:
        return [], diff_headers, []

    diff_units = _compare_units(dlf1.units, dlf2.units)
    if len(diff_units) > 0:
        return [], diff_units, []

    
    return _compare_bodies(dlf1.body,
                           dlf2.body,
                           dlf1.units,
                           dlf1.header,
                           precision,
                           sml_identity_threshold)

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

def _compare_bodies(b1, b2, units, header, precision, sml_identity_threshold):
    # pylint: disable=too-many-arguments
    not_similar = []
    not_identical = []
    errors = []
    try:
        diff = b1.compare(b2)
        if len(diff) > 0:
            sml_map = load_smallest_meaningful_level(header, daisy_ureg)
            if len(sml_map) == 0:
                warnings.warn('No SML definitions loaded.')
            for col in diff.columns.levels[0]:
                abs_delta = (diff[col]['self'] - diff[col]['other']).abs()
                max_abs_delta_idx = abs_delta.argmax()
                delta = abs_delta.iloc[max_abs_delta_idx]
                try:
                    sml = sml_map[col]
                    delta_u = (delta * dlf_unit_to_pint_unit(units[col], daisy_ureg)).to(sml)
                    if delta_u > sml_identity_threshold * sml:
                        row = diff[col].iloc[max_abs_delta_idx]
                        msg = f'[{col}]: {row["self"]} | {row["other"]} | {delta_u} | {sml}'
                        if delta_u > sml:
                            not_similar.append(msg)
                        else:
                            not_identical.append(msg)
                except KeyError:
                    # We dont have an SML
                    warnings.warn(f'No SML for {col}')
                    if delta > sml_identity_threshold * precision:
                        row = diff[col].iloc[max_abs_delta_idx]
                        msg = f'[{col}]: {row["self"]} | {row["other"]} | {delta} | {precision}'
                        if delta > precision:
                            not_similar.append(msg)
                        else:
                            not_identical.append(msg)
                except UndefinedUnitError:
                    errors.append(f'Unknown unit {units[col]} for {col}')
                except AttributeError:
                    errors.append(f'Unit conversion error {units[col]} for {col}')
                except DimensionalityError:
                    errors.append(f'Unit mismatch {units[col]} !~ {sml_map[col]} for {col}')
    except ValueError as e:
        errors.append(e)

    return errors, not_similar, not_identical
