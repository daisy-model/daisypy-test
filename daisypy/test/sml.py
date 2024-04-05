'''Smallest meaningful levels (SMLs) are used during testing. Differences less than 1 SML are
considered irrelevant for testing purposes.'''
import os
import warnings
import tomllib

import pint

__all__ = [
    'load_smallest_meaningful_level'
]

def load_smallest_meaningful_level(names, ureg):
    '''Load smallest meaningful level (SML) definition.

    Parameters
    ----------
    names :list of str OR str
      Either a list of SML definition names or a single SML definition name

    Returns
    -------
    dict of SML definitions or empty dict if unable to load
    '''
    sml_paths = {
        'harvest' : 'sml-definitions/harvest.toml',
        'Field nitrogen' : 'sml-definitions/field_nitrogen.toml',
        'Soil nitrogen' : 'sml-definitions/soil_nitrogen.toml',
        'Soil water' : 'sml-definitions/soil_water.toml',
        'Field water' : 'sml-definitions/field_water.toml',
        'Crop' : 'sml-definitions/crop.toml',
    }
    if not isinstance(names, list):
        names = [names]
    for name in names:
        try:
            path = os.path.join(os.path.dirname(os.path.realpath(__file__)), sml_paths[name])
            with open(path, 'rb') as infile:
                sml = tomllib.load(infile)
            for k, v in sml.items():
                sml[k] = ureg(v)
            print(f"INFO: Found SML definition for '{name}'", flush=True)
            return sml
        except (KeyError, pint.UndefinedUnitError) as e:
            warnings.warn(f'Could not load SML definition for {name}: {e}')
    return {}
