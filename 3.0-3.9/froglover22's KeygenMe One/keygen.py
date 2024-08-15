#!/usr/bin/env python
import random

def generateseed():
    numero_casuale = random.randint(0x0, 0xFFFFFFFF)
    return "{:08X}".format(numero_casuale)

def checklen(in_serial):
    if len(in_serial) == 24:
        return True
    else:
        return False

def computehash(in_serial):
    len_serial = len(in_serial)
    print("serial is %s" % in_serial)
    print("len serial is %d" % len_serial)
    dl = 0xAF
    bl = 0x56
    for ii in range(0, len_serial, 4):  
        print("taking char %s as val %x" % (in_serial[ii],ord(in_serial[ii])))
        dl = (dl + ord(in_serial[ii])) & 0xFF
        print("1: dl is 0x%x" % dl)
        bl = (bl + dl) & 0xFF
        print("2: bl is 0x%x" % bl)
        dl = (dl + ord(in_serial[ii+1])) & 0xFF
        print("3: dl is 0x%x" % dl)
        bl = ( bl + dl ) & 0xFF
        print("4: bl is 0x%x" % bl)
        dl = ( dl + ord(in_serial[ii+2])  & 0xFF)
        print("5: dl is 0x%x" % dl)
        bl = ( bl + dl ) & 0xFF
        print("6: bl is 0x%x" % bl)
        dl = ( dl + ord(in_serial[ii+3]) ) & 0xFF
        print("7: dl is 0x%x" % dl)
        bl = ( bl + dl ) & 0xFF
        print("8: bl is 0x%x" % bl)
        print("[%d]: (bl,dl) is (0x%x,0x%x)" % (ii,bl,dl))
    eax = bl << 8
    print("9: eax is 0x%x" % eax)
    ## sign extend, quick and dirty, check if 8-bit is one by masking with binary 10000000 and then to compare to 1, remove 7 bits from right
    if ((dl & (0x1<<7)) >> 7) == 0x1:
        ecx = dl + 0xFFFFFF00   
    else:
        ecx = dl

    print("10: ecx is 0x%x" % ecx)
    ecx = (eax + ecx) & 0xFFFF
    print("11: ecx is 0x%x" % ecx)
    #ecx = "{:0>4}".format(ecx)
    ecx = "{:04X}".format(ecx)
    return ecx.lower() # i prefer lowercase since in this case doesn't matter

def computechecksum(first_serial):
    ret_checksum = bytearray([])
    table = [ 0x3, 0x5, 0x9, 0x6, 0xa, 0xc, 0x0 ]
    table2 = { 0x3: 0, 0x5: 0, 0x9: 0, 0x6: 1,  0xa: 1, 0xc: 2, 0x0: 3 }

    key_check_pairs = bytearray([0x3, 0x5, 0x9, 0x6, 0xa, 0xc])
    lookup_tbl1 = bytearray([0x8, 0xa, 0xc, 0xe])
    lookup_tbl2 = bytearray([0xa, 0xc, 0xe, 0x10])

    lookup_tbl3 = bytearray([0x18, 0xa, 0x1, 0x7])
    lookup_tbl4 = bytearray([0x3, 0x0, 0x2, 0x1])
    lookup_tbl5 = bytearray([0xc8, 0x38, 0x5b, 0x64])
    r12 = int(first_serial,base=16)
    # for numero in range(0, 6):  
    for numero in [ 0, 3, 5, 6 ]:  
        print("-----")
        print("numero è %d" % numero)

        r15 = table2[table[numero]]
        print("r15 è %x" % r15)
        r13d = lookup_tbl1[r15]
        val_tbl2 = lookup_tbl2[r15]
        val_tbl3 = lookup_tbl3[r15]
        val_tbl4 = lookup_tbl4[r15]
        val_tbl5 = lookup_tbl5[r15]

        #string_tohash = first_serial[r13d:val_tbl2] # length 2 and r13d > 8, due to the lookup tables
        #string_tohash_d = ord(string_tohash[0])*100+ord(string_tohash[1])

        temp_val_esi = val_tbl3 * 5 * 8 + val_tbl3 
        print("temp_val[2] è 0x%x" % temp_val_esi)

        temp_val_esi = (temp_val_esi >> 0x10) & 0xffffffffffffffff
        print("temp_val[3] è 0x%x" % temp_val_esi)

        temp_val_esi = temp_val_esi * 5 * 5
        print("temp_val[4] è 0x%x" % temp_val_esi)

        temp_val_cl = val_tbl3 - temp_val_esi
        print("temp_val_cl[5] è 0x%x" % temp_val_cl)

        temp_val_esi = val_tbl4 * 0xAB # eax == 0 
        print("temp_val[6] è 0x%x" % temp_val_esi)

        temp_val_esi = (temp_val_esi >> 0x9) & 0xffffffffffffffff
        print("temp_val[7] è 0x%x" % temp_val_esi)

        temp_val_esi = temp_val_esi * 3
        print("temp_val[8] è 0x%x" % temp_val_esi)

        temp_val_ax = val_tbl4 - temp_val_esi
        print("temp_val[9] è 0x%x" % temp_val_ax) 

        temp_val_esi = ( r12 >> temp_val_cl )
        print("temp_val[10] è 0x%x" % temp_val_esi)

        # test cl, 1
        if (temp_val_cl & 0x1) == 1:
            print("temp_val_cl == 1")
            temp_val_edi = ( r12 >> temp_val_ax )
            print("temp_val[11] è 0x%x" % temp_val_edi)
            
            temp_val_edx = val_tbl5 & temp_val_edi
            print("temp_val[12] è 0x%x" % temp_val_edx)

            temp_val_edx = temp_val_edx ^ temp_val_esi
            print("temp_val[13] è 0x%x" % temp_val_edx) 

            temp_val_edi = temp_val_edx
        else:
            print("not jumped")
            temp_val_edi = ( r12 >> temp_val_ax )
            print("temp_val[11] è 0x%x" % temp_val_edi)
            
            temp_val_edi = temp_val_edi | val_tbl5
            print("temp_val[12] è 0x%x" % temp_val_edi)

            temp_val_edi = temp_val_edi ^ (temp_val_esi & 0xFF)
            print("temp_val[13] è 0x%x" % temp_val_edi)

        print("s1 è %x" % (temp_val_edi & 0xff))
        ret_checksum.append((temp_val_edi & 0xff))

    #print("done")
    #for jj in ret_checksum:
    #    print("el is %x" % jj)
    str_checksum = "".join([ "{:02x}".format(kk) for kk in ret_checksum ])
    return str_checksum

in_serial = generateseed()
#in_serial = "12345678"
checksum = computechecksum(in_serial)
hashed = computehash(in_serial + checksum)
print("hash is %s" % hashed)
print("")
print("the serial is:")
print(in_serial + checksum + hashed + "asdf")
