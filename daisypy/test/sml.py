'''Smallest meaningful levels (SMLs) are used during testing. Differences less than 1 SML are
considered irrelevant for testing purposes.'''
import os
import tomllib

import pint

__all__ = [
    'load_smallest_meaningful_level'
]


sml_paths = {
    'Field chemical' : 'sml-definitions/field_chemicals.toml',
    'Soil chemical' : 'sml-definitions/soil_chemicals.toml',
    
    'Field chemical N' : 'sml-definitions/field_chemicals_N.toml',
    'Soil chemical N' : 'sml-definitions/soil_chemicals_N.toml',
    
    'Field nitrogen' : 'sml-definitions/field_nitrogen.toml',
    'Soil nitrogen' : 'sml-definitions/soil_nitrogen.toml',
    
    'Soil water' : 'sml-definitions/soil_water.toml',
    'Field water' : 'sml-definitions/field_water.toml',
    
    'Crop' : 'sml-definitions/crop.toml',
}

def load_smallest_meaningful_level(header, ureg):
    '''Load smallest meaningful level (SML) definition.

    Parameters
    ----------
    header: dict
      Header from a dlf file

    Returns
    -------
    dict of SML definitions or empty dict if unable to load
    '''
    names = []
    if 'chemical' in header['dlf-component'] and 'CHEMICAL' in header:
        names.append(f"{header['dlf-component']} {header['CHEMICAL']}")
    names.append(header['dlf-component'])
    for name in names:
        try:
            path = os.path.join(os.path.dirname(os.path.realpath(__file__)), sml_paths[name])
            with open(path, 'rb') as infile:
                sml = tomllib.load(infile)
            for k, v in sml.items():
                sml[k] = ureg(v)
            return sml
        except (KeyError, pint.UndefinedUnitError):
            pass
    return {}
