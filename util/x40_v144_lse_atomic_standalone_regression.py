#!/usr/bin/env python3
"""Standalone AArch64 LSE vs STUR/STTR discriminator, synthetic opcodes only."""
LSE = (0xb823003f, 0xf823003f, 0xb8230024, 0xf8230024,
       0xf8e30024, 0xb8238024, 0xf8238024, 0xf8e38024,
       0x3823003f, 0x38230024, 0x7823003f, 0x78230024)
OTHER = (0xc8a37c24, 0xc89ffc23, 0xc8dffc23,
         0xf8030823, 0xf8430823, 0xf8030023, 0xf8226823,
         0xf9001823, 0xf9401823)

def lse_family(word):
    return ((word & 0x3f000000) == 0x38000000
            and (word >> 21) & 1 == 1 and ((word >> 10) & 3) == 0)

def prior_false_offset(word):
    offset = (word >> 12) & 0x1ff
    if offset & 0x100:
        offset -= 0x200
    return offset

def test():
    for word in LSE:
        assert lse_family(word)
    for word in OTHER:
        assert not lse_family(word)
    phantom = [w for w in LSE if ((w >> 22) & 1) == 0 and 0x30 - (1 << ((w >> 30) & 3)) + 1 <= prior_false_offset(w) < 0x38]
    assert len(phantom) == 8, len(phantom)
    assert lse_family(0xf8230024) and prior_false_offset(0xf8230024) == 0x30
    assert not lse_family(0xf8030823)  # Real STTR x3,[x1,#48]
    assert not lse_family(0xf8030023)  # Real STUR x3,[x1,#48]
    print('X40_V144_LSE_STANDALONE_PASS opcode_samples=21 synthetic_phantom_overlaps=8')

if __name__ == '__main__':
    test()
