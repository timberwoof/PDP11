'''pdp 11 emulator utilities'''

def oct3(word):
    """format an octal to be 6 digits wide:
    0o2127 -> 0o002127"""
    octal = oct(word)[2:]
    padding_zeroes = '0000'[0:3-len(octal)]
    result = f'{padding_zeroes}{octal}'
    return result

def oct6(word):
    """format an octal to be 6 digits wide:
    0o2127 -> 0o002127"""
    octal = oct(word)
    padding_zeroes = '000000'[0:8 - len(octal)]
    result = f'{octal[2:2]}{padding_zeroes}{octal[2:]}'
    return result

def pad(string, width):
    """pad a string to width charactcers"""
    padding = '                    '[0:width - len(string)]
    result = f'{string}{padding}'
    return result
