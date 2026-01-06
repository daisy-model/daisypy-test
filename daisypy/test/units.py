'''Unit conversion and a minimal unit registry for use when testing Daisy

 The default registry is quite large and takes around 0.5s to load. We only need a small part of
 those units, so we just copy the relevant parts from pint/default_en.txt
'''
from functools import reduce
import pint

__all__ = [
    'daisy_ureg',
    'dlf_unit_to_pint_unit'
]

unit_registry = [
    'micro- = 1e-6  = u-',
    'milli- = 1e-3  = m-',
    'centi- = 1e-2  = c-',
    'deci- =  1e-1  = d-',
    'kilo- =  1e3   = k-',
    'mega- =  1e6   = M-',
    'giga- =  1e9   = G-',

    'meter = [length] = m = metre',
    'second = [time] = s = sec',
    'gram = [mass] = g',

    'minute = 60 * second = min',
    'hour = 60 * minute = h = hr',
    'day = 24 * hour = d',
    'year = 365.25 * day = a = yr = julian_year',
    'month = year / 12',

    'hectare = 10000 m^2 = ha',

    'ppm = 1e-6',

    '[velocity] = [length] / [time]',
    '[acceleration] = [velocity] / [time]',
    '[force] = [mass] * [acceleration]',
    '[energy] = [force] * [length]',
    'newton = kilogram * meter / second ** 2 = N',
    'joule = newton * meter = J',
]

daisy_ureg = pint.UnitRegistry(unit_registry)

def dlf_unit_to_pint_unit(unit, ureg):
    '''Convert a unit from a dlf file to a pint unit. Units in dlf files can for example be given as
      kg N/ha = kg nitrogen per hectare
    pint does not understand the nitrogen part, so we need to strip it

    Parameters
    ----------
    unit: str
      dlf unit specification

    Returns
    -------
    pint.Quantity

    '''
    if unit in {'', 'DS'}:
        return ureg('dimensionless')
    redefine = {
        ' DM/ha' : '/ha',
        ' N/ha' : '/ha',
        ' C/ha' : '/ha',
        'ppm dry soil' : 'ppm',
    }
    # Apply all redefinitions to the unit
    redefined_unit = reduce(lambda s, kv: s.replace(kv[0], kv[1]), redefine.items(), unit)

    # Convert to pint unit
    return ureg(redefined_unit)
