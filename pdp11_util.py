'''pdp 11 emulator utilities'''
import logging

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

def twosComplementNegative(source):
    """Convert positive word to 2's completemt negative word"""
    # invert bits and add 1 (then mask_word for PDP11ness)
    result = (~source + 1) & MASK_WORD
    logging.info(f'twosComplementNegative({oct(source)}) returns {oct(result)}')
    return result

def pythonifyPDP11Word(source):
    """convert PDP11 integer which may be 2's complement negative to pythonish integer"""
    # If it's a PDP11 positive, just return that
    # If it's a PDP11 negative, then
    #    extend the bits, subtract 1, invert
    result = source
    if (MASK_WORD_MSB & source) == MASK_WORD_MSB:
        result = -~((source | ~MASK_WORD) - 1)
    logging.info(f'pythonifyPDP11Word({oct(source)}) returns {result}')
    return result

def PDP11ifyPythonInt(source):
    """convert a positive or negative Pyton integer to PDP-11 word"""
    result = 0
    if source >= 0:
        result = source & MASK_WORD
    else:
        result = twosComplementNegative(-source)
    logging.info(f'PDP11ifyPythonInt({oct(source)}) returns {oct(result)}')
    return result

def extendSign(source):
    """convert word with sign but set to python negative integer"""
    result = source
    if (MASK_WORD_MSB & source) == MASK_WORD_MSB:
        result = source & ~0
    return result

