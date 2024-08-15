#!/usr/bin/env python
import random
serial = '12345678ea6d2688b68basdf'
verbose = 0

def printv(string_toprint):
    if verbose == 1:
        print(string_toprint)

def checkhash(serial):
    in_serial = serial.replace('-', '')
    len_serial = len(in_serial)
    if len_serial == 0:
        return false
    last_part_serial = 0
    first_part_serial = 0
    len_first_part_serial = 0
    if len_serial >= 0x11:
        last_part_serial = in_serial[0x10:]
        first_part_serial = in_serial[0:0x10]
        len_first_part_serial = len(first_part_serial)
    if len(last_part_serial) > 4:
        last_part_serial = last_part_serial[0:4]
    
    printv("serial is %s" % in_serial)
    printv("len serial is %d" % len_serial)
    dl = 0xAF
    bl = 0x56
    rem = len_first_part_serial % 4
    if len_first_part_serial >= 4:
        for ii in range(0, len_first_part_serial, 4):
            printv("taking char %s as val %x" % (first_part_serial[ii],ord(first_part_serial[ii])))
            dl = (dl + ord(first_part_serial[ii])) & 0xFF
            printv("1: dl is 0x%x" % dl)
            bl = (bl + dl) & 0xFF
            printv("2: bl is 0x%x" % bl)
            dl = (dl + ord(first_part_serial[ii+1])) & 0xFF
            printv("3: dl is 0x%x" % dl)
            bl = ( bl + dl ) & 0xFF
            printv("4: bl is 0x%x" % bl)
            dl = ( dl + ord(first_part_serial[ii+2])  & 0xFF)
            printv("5: dl is 0x%x" % dl)
            bl = ( bl + dl ) & 0xFF 
            printv("6: bl is 0x%x" % bl)
            dl = ( dl + ord(first_part_serial[ii+3]) ) & 0xFF
            printv("7: dl is 0x%x" % dl)
            bl = ( bl + dl ) & 0xFF
            printv("8: bl is 0x%x" % bl)
            printv("[%d]: (bl,dl) is (0x%x,0x%x)" % (ii,bl,dl))

    if rem != 0:
        printv("found remaingin!")
        for ii in range(0, rem):
            dl = (dl + ord(first_part_serial[ii])) & 0xFF
            bl = (bl + dl) & 0xFF

    eax = bl << 8
    printv("9: eax is 0x%x" % eax)
    ## sign extend, quick and dirty, check if 8-bit is one by masking with binary 10000000 and then to compare to 1, remove 7 bits from right
    if ((dl & (0x1<<7)) >> 7) == 0x1:
        ecx = dl + 0xFFFFFF00
    else:
        ecx = dl

    printv("10: ecx is 0x%x" % ecx)
    ecx = (eax + ecx) & 0xFFFF 
    printv("11: ecx is 0x%x" % ecx)
    #ecx = "{:0>4}".format(ecx)
    ecx = "{:04X}".format(ecx).lower() # i prefer lowercase since in this case doesn't matter
    printv("[%s] == [%s]" % (ecx, last_part_serial))
    return ecx == last_part_serial

if not checkhash(serial):
    print("wrong hash")
    exit(1)
nptr_pos = 8
nptr = serial[0:nptr_pos]
r12 = int(nptr,base=16) # strtol
hashtocheck = serial[nptr_pos:0x10]
numerorandom = random.randint(0,6)
for numero in range(numerorandom, 7):
    table = [ 0x3, 0x5, 0x9, 0x6, 0xa, 0xc, 0x0 ]
    table2 = { 0x3: 0, 0x5: 0, 0x9: 0, 0x6: 1,  0xa: 1, 0xc: 2, 0x0:3 }

    key_check_pairs = bytearray([0x3, 0x5, 0x9, 0x6, 0xa, 0xc])
    lookup_tbl1 = bytearray([0x8, 0xa, 0xc, 0xe])
    lookup_tbl2 = bytearray([0xa, 0xc, 0xe, 0x10])
    
    lookup_tbl3 = bytearray([0x18, 0xa, 0x1, 0x7])
    lookup_tbl4 = bytearray([0x3, 0x0, 0x2, 0x1])
    lookup_tbl5 = bytearray([0xc8, 0x38, 0x5b, 0x64])
    
    r15 = table2[table[numero]]
    r13d = lookup_tbl1[r15]
    val_tbl2 = lookup_tbl2[r15]
    string_tohash = serial[r13d:val_tbl2] # length 2 and r13d > 8, due to the lookup tables
    string_tohash_d = ord(string_tohash[0])*100+ord(string_tohash[1])
    hashtocheck_single = hashtocheck[r15*2:r15*2+2]
    
    val_tbl3 = lookup_tbl3[r15]
    val_tbl4 = lookup_tbl4[r15]
    val_tbl5 = lookup_tbl5[r15]
    
    temp_val_esi = val_tbl3 * 5 * 8 + val_tbl3 
    printv("temp_val[2] è 0x%x" % temp_val_esi)
    
    temp_val_esi = (temp_val_esi >> 0x10) & 0xffffffffffffffff
    printv("temp_val[3] è 0x%x" % temp_val_esi)
    
    temp_val_esi = temp_val_esi * 5 * 5
    printv("temp_val[4] è 0x%x" % temp_val_esi)
    
    temp_val_cl = val_tbl3 - temp_val_esi
    printv("temp_val_cl[5] è 0x%x" % temp_val_cl)
    
    temp_val_esi = val_tbl4 * 0xAB # eax == 0 
    printv("temp_val[6] è 0x%x" % temp_val_esi)
    
    temp_val_esi = (temp_val_esi >> 0x9) & 0xffffffffffffffff
    printv("temp_val[7] è 0x%x" % temp_val_esi)
    
    temp_val_esi = temp_val_esi * 3
    printv("temp_val[8] è 0x%x" % temp_val_esi)
    
    temp_val_ax = val_tbl4 - temp_val_esi
    printv("temp_val[9] è 0x%x" % temp_val_ax)
    
    temp_val_esi = ( r12 >> temp_val_cl )
    printv("temp_val[10] è 0x%x" % temp_val_esi)
    
    # test cl, 1
    if (temp_val_cl & 0x1) == 1:
        printv("temp_val_cl == 1")
        temp_val_edi = ( r12 >> temp_val_ax )
        printv("temp_val[11] è 0x%x" % temp_val_edi)
    
        temp_val_edx = val_tbl5 & temp_val_edi
        printv("temp_val[12] è 0x%x" % temp_val_edx)
    
        temp_val_edx = temp_val_edx ^ temp_val_esi
        printv("temp_val[13] è 0x%x" % temp_val_edx)
    
        temp_val_edi = temp_val_edx
    else:
        printv("not jumped")
        temp_val_edi = ( r12 >> temp_val_ax )
        printv("temp_val[11] è 0x%x" % temp_val_edi)
    
        temp_val_edi = temp_val_edi | val_tbl5
        printv("temp_val[12] è 0x%x" % temp_val_edi)
        
        temp_val_edi = temp_val_edi ^ (temp_val_esi & 0xFF)
        printv("temp_val[13] è 0x%x" % temp_val_edi)
    
    printv("s1 è %x" % (temp_val_edi & 0xff))
    printv("s2 è %s" % string_tohash )
    
    printv("nptr è %s" % nptr)
    printv("numero è %d" % numero)
    printv("r15 è %d" % r15)
    printv("r13d è %d" % r13d)
    printv("val_tbl2 è %d" % val_tbl2)
    printv("val_tbl3 è 0x%x" % val_tbl3)
    printv("val_tbl4 è 0x%x" % val_tbl4)
    printv("val_tbl5 è 0x%x" % val_tbl5)
    printv("string_tohash è %s" % string_tohash)
    printv("hashtocheck è %s" % hashtocheck)
    printv("hashtocheck_single è %s" % hashtocheck_single)
    
    if hashtocheck_single != string_tohash:
        print("Wrong serial")
        exit(1)
print("[%s] is a valid serial!" % serial )
