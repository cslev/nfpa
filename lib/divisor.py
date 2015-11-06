'''
This python file is resplonsible only for converting units into number, e.g.,
when unit is set to G, then it returns 1000000000
'''
   
def divisor(unit):
    '''
    This process returns the divisor for results according to the units.
    For instance, if unit='G', then this returns 1.000.000.000.
    return divisor - float
    '''
    #prepare for case insensitivity
    #Kilo
    if unit.lower() == "k":
        return 1000.0
    #Mega
    elif unit.lower() == "m":
        return 1000000.0
    #Giga
    elif unit.lower() == "g":
        return 1000000000.0
    #in case of something was set, but there is no definition for it, then we
    #stick to the default value (this is the same case, when it is None
    else:
        return 1
    