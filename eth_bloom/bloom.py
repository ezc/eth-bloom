from __future__ import absolute_import

import operator
import numbers

try:
    from sha3 import keccak_256
except ImportError:
    from sha3 import sha3_256 as keccak_256


assert keccak_256(b'').digest() == b"\xc5\xd2F\x01\x86\xf7#<\x92~}\xb2\xdc\xc7\x03\xc0\xe5\x00\xb6S\xca\x82';\x7b\xfa\xd8\x04\x5d\x85\xa4p", "Incorrect sha3.  Make sure it's keccak"  # noqa: E501


def get_chunks_for_bloom(value_hash):
    yield value_hash[:2]
    yield value_hash[2:4]
    yield value_hash[4:6]


def chunk_to_bloom_bits(chunk):
    high, low = bytearray(chunk)
    return 1 << ((low + (high << 8)) & 2047)


def get_bloom_bits(value):
    value_hash = keccak_256(value).digest()
    for chunk in get_chunks_for_bloom(value_hash):
        bloom_bits = chunk_to_bloom_bits(chunk)
        yield bloom_bits


class BloomFilter(numbers.Number):
    value = None

    def __init__(self, value=0):
        self.value = value

    def __int__(self):
        return self.value

    def add(self, value):
        if not isinstance(value, bytes):
            raise TypeError("Value must be of type `bytes`")
        for bloom_bits in get_bloom_bits(value):
            self.value |= bloom_bits

    def __contains__(self, value):
        if not isinstance(value, bytes):
            raise TypeError("Value must be of type `bytes`")
        return all(
            self.value & bloom_bits
            for bloom_bits in get_bloom_bits(value)
        )

    def __index__(self):
        return operator.index(self.value)