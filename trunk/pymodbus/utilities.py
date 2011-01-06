'''
Modbus Utilities
-----------------

A collection of utilities for packing data, unpacking
data computing checksums, and decode checksums.
'''

def default(value):
    '''
    Given a python object, return the default value
    of that object.

    :param value: The value to get the default of
    :returns: The default value
    '''
    return type(value)()

def packBitsToString(bits):
    ''' Creates a string out of an array of bits

    :param bits: A bit array

    example::

        bits = [False, True, False, True]
        result = packBitsToString(bits)
    '''
    ret = ''
    i = packed = 0
    for bit in bits:
        if bit: packed += 128
        i += 1
        if i == 8:
            ret += chr(packed)
            i = packed = 0
        else: packed >>= 1
    if i > 0 and i < 8:
        packed >>= 7-i
        ret += chr(packed)
    return ret

def unpackBitsFromString(string):
    ''' Creates bit array out of a string

    :param string: The modbus data packet to decode

    example::

        string[0]   = bytes to follow
        string[1-N] = bytes to decode
    '''
    byte_count = ord(string[0])
    bits = []
    for byte in range(1, byte_count+1):
        value = ord(string[byte])
        for bit in range(8):
            bits.append((value & 1) == 1)
            value >>= 1
    return bits, byte_count

#---------------------------------------------------------------------------#
# Error Detection Functions
#---------------------------------------------------------------------------#
def __generate_crc16_table():
    ''' Generates a crc16 lookup table

    .. note:: This will only be generated once
    '''
    result = []
    for byte in range(256):
        crc = 0x0000
        for bit in range(8):
            if (byte ^ crc) & 0x0001:
                crc = (crc >> 1) ^ 0xa001
            else: crc >>= 1
            byte >>= 1
        result.append(crc)
    return result

__crc16_table = __generate_crc16_table()

def computeCRC(data):
    ''' Computes a crc16 on the passed in string. For modbus,
    this is only used on the binary serial protocols (in this
    case RTU).

    The difference between modbus's crc16 and a normal crc16
    is that modbus starts the crc value out at 0xffff.

    :param data: The data to create a crc16 of
    :returns: The calculated CRC
    '''
    crc = 0xffff
    for a in data:
        idx = __crc16_table[(crc ^ ord(a)) & 0xff];
        crc = ((crc >> 8) & 0xff) ^ idx
    return crc

def checkCRC(data, check):
    ''' Checks if the data matches the passed in CRC

    :param data: The data to create a crc16 of
    :param check: The CRC to validate
    :returns: True if matched, False otherwise
    '''
    return computeCRC(data) == check

def computeLRC(data):
    ''' Used to compute the longitudinal redundancy check
    against a string. This is only used on the serial ASCII
    modbus protocol. A full description of this implementation
    can be found in appendex B of the serial line modbus description.

    :param data: The data to apply a lrc to
    :returns: The calculated LRC

    '''
    lrc = 0
    lrc = sum(ord(a) for a in data) & 0xff
    lrc = (lrc ^ 0xff) + 1
    return lrc

def checkLRC(data, check):
    ''' Checks if the passed in data matches the LRC

    :param data: The data to calculate
    :param check: The LRC to validate
    :returns: True if matched, False otherwise
    '''
    return computeLRC(data) == check

#---------------------------------------------------------------------------# 
# Exported symbols
#---------------------------------------------------------------------------# 
__all__ = [
    'packBitsToString', 'unpackBitsFromString', 'default',
    'computeCRC', 'checkCRC', 'computeLRC', 'checkLRC'
]
