'''pdp 11 emulator utilities'''
MASK_WORD = 0o177777
MASK_BYTE = 0o000377
MASK_WORD_MSB = 0o100000

def oct3(word):
    """format an octal to be 6 digits wide:
    0o27 -> 027"""
    octal = oct(word)[2:]
    padding_zeroes = '0000'[0:3-len(octal)]
    result = f'{padding_zeroes}{octal}'
    return result

def oct6(word):
    """format an octal to be 6 digits wide:
    0o2127 -> 002127"""
    octal = oct(word)
    padding_zeroes = '000000'[0:8 - len(octal)]
    result = f'{octal[2:2]}{padding_zeroes}{octal[2:]}'
    return result

def pad(string, width):
    """right-pad a string to width charactcers"""
    padding = '                    '[0:width - len(string)]
    result = f'{string}{padding}'
    return result

def twosCompletentNegative(source):
    """Convert positive word to 2's completemt negative word"""
    return (~source + 1) & MASK_WORD

def extendSign(source):
    """convert word with sign but set to python negative integer"""
    result = source
    if (MASK_WORD_MSB & source) == MASK_WORD_MSB:
        result = source & ~0
    return result
