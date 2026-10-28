#!/usr/bin/env python3
"""Offline, source-free AArch64 STTR/LDTR opcode regression; never accesses device."""
def decode_sttr(word):
    if (word & 0x3f000000)!=0x38000000 or (word>>22)&1 or (word>>21)&1 or ((word>>10)&3)!=2:
        return None
    imm=(word>>12)&511
    if imm&256:imm-=512
    return {'offset':imm,'width':1<<((word>>30)&3),'base':(word>>5)&31}

def overlaps(offset,width,start=0x30,end=0x38):
    return offset<end and offset+width>start

def test():
    positives=[(0xf8030823,8),(0xb8030823,4),(0x38030823,1),(0x78030823,2)]
    negatives=[0xf8430823,0xb8430823,0x38430823,0x78430823]
    checks=0
    for w,width in positives:
        x=decode_sttr(w)
        assert x=={'offset':48,'width':width,'base':1}
        assert overlaps(x['offset'],x['width'])
        checks+=2
    for w in negatives:
        assert decode_sttr(w) is None
        checks+=1
    for off,want in [(40,False),(41,True),(48,True),(55,True),(56,False),(-1,False)]:
        w=(positives[0][0]&~(511<<12))|((off&511)<<12)
        x=decode_sttr(w)
        assert x is not None and x['offset']==off and overlaps(off,x['width'])==want
        checks+=1
    for w,_ in positives:
        assert decode_sttr(w|(1<<22)) is None
        checks+=1
    print('X40_V143_STTR_STANDALONE_OPCODE_TEST_PASS assertions='+str(checks))
if __name__=='__main__':test()
