def EnumToString(cl, value):
    keys = [k for k in dir(cl) if k[0] != '_' ]
    for key in keys:
        if getattr(cl, key) == value:
            return key
    raise RuntimeError('Value "{}" is not part of the enum "{}".'.format(value, cl.__name__))
    
def ParseEnum(cl, str_value):
    keys = [k for k in dir(cl) if k[0] != '_' ]
    for key in keys:
        if key == str_value:
            return getattr(cl, key)
    raise RuntimeError('String "{}" can\'t be parsed as an element of enum "{}".'.format(str_value, cl.__name__))

class TauSelection:
    gen = 1
    pt = 2
    MVA = 4
    DeepTau = 8
