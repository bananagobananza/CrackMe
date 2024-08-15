The program is an exe named *one*, to be executed on a linux machine, with the following details:

```
Input SHA256 : B3B7FF77796617E36036550CD17F03BC96E9D062EDC3C1570E81048653D19B3D
Input MD5    : 37C5949ED8D17849613FB32C878540D3
Input CRC32  : 615D8D42

File Name   : one
Size        : 17K
Format      : ELF64 for x86-64 (Shared object)
Interpreter : '/lib64/ld-linux-x86-64.so.2'
Library used: 'libc.so.6'
Scope       : to write a keygen for the crackme
```

a brief analysis using readelf reveals nothing of strange, .init and .init_array section are clean exactly as .fini and .fini_array and even frame_dummy,gmon_start/stop and cxa_finalize are standard. The interpreter is the usual one
spawing "strings one" suggests that was written in c from a source named one.c and compiled with [GCC: (Debian 12.2.0-14) 12.2.0] or [Debian clang version 14.0.6]

the imported functions are the following: __libc_start_main, strcpy, puts, stdin, strlen, snprintf, srand, fgets, strcmp, strtoll, time, rand, cxa_finalize, ITM_deregisterTMCloneTable, gmon_start, ITM_registerTMCloneTable
The "stdin" is an indicator that the serial will be read from a prompt and not from a file, "time" could be an indicator of an antidebugging trick or as seed to rand (see later)

as expected, ghydra/ida/radare2 show at the entry point the libc_start external call

```
.text:00005555555550E0    xor     ebp, ebp
.text:00005555555550E2    mov     r9, rdx         ; rtld_fini
.text:00005555555550E5    pop     rsi             ; argc
.text:00005555555550E6    mov     rdx, rsp        ; ubp_av
.text:00005555555550E9    and     rsp, 0FFFFFFFFFFFFFFF0h
.text:00005555555550ED    push    rax
.text:00005555555550EE    push    rsp             ; stack_end
.text:00005555555550EF    xor     r8d, r8d        ; fini
.text:00005555555550F2    xor     ecx, ecx        ; init
.text:00005555555550F4    lea     rdi, main       ; main
.text:00005555555550FB    call    cs:__libc_start_main_ptr
.text:0000555555555101    hlt
```

the main function, on the rdi register:

```
.text:0000555555555990     push    rbx
.text:0000555555555991     sub     rsp, 40h
.text:0000555555555995     lea     rdi, s          ; "Enter your serial number: "
.text:000055555555599C     call    _puts
.text:00005555555559A1     xorps   xmm0, xmm0
.text:00005555555559A4     movaps  [rsp+48h+var_18], xmm0
.text:00005555555559A9     movaps  [rsp+48h+var_28], xmm0
.text:00005555555559AE     movaps  [rsp+48h+var_38], xmm0
.text:00005555555559B3     movaps  [rsp+48h+var_48], xmm0
.text:00005555555559B7     mov     rax, cs:stdin_ptr
.text:00005555555559BE     mov     rdx, [rax]      ; stream
.text:00005555555559C1     mov     rbx, rsp
.text:00005555555559C4     mov     rdi, rbx        ; s
.text:00005555555559C7     mov     esi, 40h ; '@'  ; n
.text:00005555555559CC     call    _fgets
.text:00005555555559D1     mov     rdi, rbx        ; s
.text:00005555555559D4     call    _strlen
.text:00005555555559D9     add     eax, 0FFFFFFFFh
.text:00005555555559DC     cdqe
.text:00005555555559DE     mov     byte ptr [rsp+rax+48h+var_48], 0 ; var_48+48h=0 => rsp+rax point last character of input string
.text:00005555555559E2     mov     rdi, rbx        ; 
.text:00005555555559E5     call    pkv_check_key   ; rdi=serial 
.text:00005555555559EA     lea     rcx, aSerialNumberIs ; "Serial number is valid!"
.text:00005555555559F1     lea     rdi, aSerialNumberIs_0 ; "Serial number is invalid. Please try ag"...
.text:00005555555559F8     test    al, al          ; al==0?
.text:00005555555559FA     cmovnz  rdi, rcx        ; move if not zero ZN
.text:00005555555559FE     call    _puts           ; if al!=0 then solved!
.text:0000555555555A03     xor     eax, eax
.text:0000555555555A05     add     rsp, 40h
.text:0000555555555A09     pop     rbx
.text:0000555555555A0A     retn
```

basically prompt for a serial, read from stdin it, call "pkv_check_key" function with serial on rdi. Before returning main clear the stack, restore rbx and set rax to zero, this suggests some info on calling convention. I will assume the usual one from now on. The point to solve the crackme is to have pkv_check_key return a value in rax different from zero

here is a part of pkv_check_key:

```
.text:0000555555555670     push    rbp
.text:0000555555555671     push    r15
.text:0000555555555673     push    r14
.text:0000555555555675     push    r13
.text:0000555555555677     push    r12
.text:0000555555555679     push    rbx
.text:000055555555567A     sub     rsp, 38h
.text:000055555555567E     lea     rsi, [rsp+68h+out_serial] ; destcopy
.text:0000555555555683     call    pkv_check_checksum
.text:0000555555555688     test    al, al          ; if eax==0 then...
.text:000055555555568A     jz      error_exit      ; ... jmp to error_exit

.text:0000555555555772     error_exit
.text:0000555555555772     xor     ebp, ebp
.text:0000555555555774     jmp     loc_555555555929

.text:0000555555555929     loc_555555555929:                      
.text:0000555555555929     and     bpl, 1          
.text:000055555555592D     mov     eax, ebp        
.text:000055555555592F     add     rsp, 38h
.text:0000555555555933     pop     rbx
.text:0000555555555934     pop     r12
.text:0000555555555936     pop     r13
.text:0000555555555938     pop     r14
.text:000055555555593A     pop     r15
.text:000055555555593C     pop     rbp
.text:000055555555593D     retn
```

it is clear than if al is zero after pkv_check_checksum, ebp will be zero (xor), anded with 1 will be 0, and eax=0. This is not what is desired, so pkv_check_checksum must return a value different from zero. rdi during the call contains the serial since the main

```
.text:00005555555551D0     push    r14
.text:00005555555551D2     push    rbx
.text:00005555555551D3     sub     rsp, 48h
.text:00005555555551D7     mov     r14, rsi
.text:00005555555551DA     mov     rbx, rdi        ; rbx=serial
.text:00005555555551DD     call    _strlen
.text:00005555555551E2     mov     rcx, rax        ; rcx=rax=len(serial)
.text:00005555555551E5     xor     eax, eax        ; eax=0
.text:00005555555551E7     cmp     rcx, 24         ; if rcx!=0x18 ...
.text:00005555555551EB     jnz     loc_555555555659; then will jump

.text:0000555555555659     loc_555555555659:       ; and return with eax=0
.text:0000555555555659     add     rsp, 48h
.text:000055555555565D     pop     rbx
.text:000055555555565E     pop     r14
.text:0000555555555660     retn    
```

From a precedent analysis, eax should be not 0 so len(serial) must be 24 (0x18)

then there is a long group of istructions:

```
.text:00005555555551F1     xorps   xmm0, xmm0      ; xmm0=0
.text:00005555555551F4     movaps  xmmword ptr [rsp+58h+stripserial], xmm0 ; init a var, I will call stripserial, first 128 bits (16 bytes)
.text:00005555555551F8     mov     qword ptr [rsp+58h+stripserial+0Dh], add terminator
.text:0000555555555201     mov     cl, [rbx]       ; rbx point to the serial, so extract the ascii value of the first char
.text:0000555555555203     cmp     cl, 2Dh ; '-'   ; compare with the ascii value for char '-'
.text:0000555555555206     jnz     loc_5555555553FD; do not jump if equal and apply same logic for other position/char
.text:000055555555520C     mov     cl, [rbx+1]
.text:000055555555520F     cmp     cl, 2Dh ; '-'
.text:0000555555555212     jnz     loc_555555555411
....
```

and in case of jump:

```
.text:00005555555553FD     loc_5555555553FD:                           ;
.text:00005555555553FD      mov     byte ptr [rsp+58h+stripserial], cl ; put ascii into var on stack stripserial
.text:0000555555555400      mov     eax, 1                             ;
.text:0000555555555405      mov     cl, [rbx+1]                        ; init/increment counter
.text:0000555555555408      cmp     cl, 2Dh ; '-'                      ; same logic of before
.text:000055555555540B      jz      loc_555555555218
```

and this logic apply for 24 (0x18) chars

```
...
.text:0000555555555314      mov     cl, [rbx+17h]
.text:0000555555555317      cmp     cl, 2Dh ; '-'
.text:000055555555531A      jz      short loc_555555555321
.text:000055555555531C     loc_55555555531C:     
.text:000055555555531C      mov     eax, eax
.text:000055555555531E      mov     byte ptr [rsp+rax+58h+stripserial], cl
```

This basically means that code is copying from original serial to a stack variable, all but the '-' char, for a total length of 24, as already guess from the first check. stripserial will be 24 char less the number of '-'

```
.text:0000555555555321      mov     rbx, rsp        ; rbx=rsp=ptr(stripserial)
.text:0000555555555324      mov     rdi, r14        ; dest
.text:0000555555555327      mov     rsi, rbx        ; src
.text:000055555555532A      call    _strcpy
.text:000055555555532F      mov     [rsp+58h+var_34], 0 ; init a support var
.text:0000555555555334      mov     dword ptr [rsp+58h+last_part_serial], 0
.text:000055555555533C      mov     rdi, rbx        ; s
.text:000055555555533F      call    _strlen         ; rax=strlen(stripserial)
.text:0000555555555344      cmp     rax, 14h        ; eax==14h?
.text:0000555555555348      mov     ecx, 14h        ; ecx=14h
.text:000055555555534D      cmovb   ecx, eax        ; if eax<14h => ecx=eax , so strlen(stripserial), so no more than ecx=14h
.text:0000555555555350      xor     edx, edx        ; edx=0
.text:0000555555555352      cmp     ecx, 11h        ; if ecx<11h ...
.text:0000555555555355      jb      short loc_555555555378 ; ...then jmp
.text:0000555555555357      add     ecx, -10h       ; ecx=ecx-10h
.text:000055555555535A      xor     edx, edx        ; edx=0
.text:000055555555535C      nop     dword ptr [rax+00h]
```

strcpy copy from stripserial to a dest var pointed by r14, at the beginning of the entire block of this function, there was this code
.text:00005555555551D7      mov     r14, rsi
considering that in rdi (esi) there is the second param, this suggest that this function is called with two parameters: serial and a pointer on the stack on which write the stripserial in order to let caller work on it

then init of two vars, for reason that will be clear in the following I will call one of them last_part_serial
compute the len of the stripserial, if len is equal or less than 16 char then it will jmp and skip the compute of the following block of code, otherwise subtract 0x10 (16) from len and set edx=0 and

```
.text:0000555555555360      movzx   ebx, byte ptr [rsp+rdx+58h+stripserial+10h] ; from 16-th char, extract ascii
.text:0000555555555365      test    bl, bl          ; if null...
.text:0000555555555367      jz      short loc_555555555378 ; ...jmp and loop exit
.text:0000555555555369      mov     [rsp+rdx+58h+last_part_serial], bl
.text:000055555555536D      add     rdx, 1          ; edx++
.text:0000555555555371      cmp     rcx, rdx        ; if rcx==rdx ... (rcx could be between 1 and 4 because is compute as 0x14 - 0x10)
.text:0000555555555374      jnz     short loc_555555555360 ; ...exit from loop
.text:0000555555555376      mov     edx, ecx
```

extract a substring from 0x10 until a terminator is found or fo no more than 4 iterations
the following code will do the same as before but copy the first part of stripserial for up to 0x10 (16) char and place it on a var that I will call first_part_serial

```
.text:0000555555555378      mov     ecx, edx
.text:000055555555537A      mov     [rsp+rcx+58h+last_part_serial], 0 ; add terminator
.text:000055555555537F      xorps   xmm0, xmm0      ; xmm0=0
.text:0000555555555382      movaps  xmmword ptr [rsp+58h+first_part_serial], xmm0
.text:0000555555555387      mov     [rsp+58h+first_part_serial_term], 0 ; add terminatore
.text:000055555555538C      cmp     rax, 10h
.text:0000555555555390      mov     ecx, 10h
.text:0000555555555395      cmovb   rcx, rax        ; rcx=10h or less (rax)
.text:0000555555555399      xor     eax, eax        ; eax=0
.text:000055555555539B      test    rcx, rcx
.text:000055555555539E      jz      short loc_5555555553B8 ; as before if zero len than skip the extraction and leave it zero (before the cmp was made with 0x11 because the interting char are placed from 0x11 position)
.text:00005555555553A0
.text:00005555555553A0     loc_5555555553A0:                      
.text:00005555555553A0      movzx   edx, byte ptr [rsp+rax+58h+stripserial]
.text:00005555555553A4      test    dl, dl
.text:00005555555553A6      jz      short loc_5555555553B8
.text:00005555555553A8      mov     [rsp+rax+58h+first_part_serial], dl
.text:00005555555553AC      add     rax, 1
.text:00005555555553B0      cmp     rcx, rax
.text:00005555555553B3      jnz     short loc_5555555553A0 ; loop for extract 16 chars
.text:00005555555553B5      mov     rax, rcx
```

if there are enough chars then copy ascii values in first_part_serial for a maximum of 16 chars

```
.text:00005555555553B8      mov     eax, eax
.text:00005555555553BA      mov     [rsp+rax+58h+first_part_serial], 0 ; add terminatore
.text:00005555555553BF      mov     [rsp+58h+var_2C], 0
.text:00005555555553C4      mov     dword ptr [rsp+58h+s2], 0
.text:00005555555553CC      lea     rdi, [rsp+58h+first_part_serial] ; s
.text:00005555555553D1      call    _strlen
.text:00005555555553D6      test    rax, rax
.text:00005555555553D9      jz      loc_5555555555CE
```

compute the len of first_part_serial, if zero then :

```
.text:00005555555555CE      mov     ecx, 55AFh
.text:00005555555555D3      jmp     short loc_55555555562C   ;

assign a value to a register (it isa checksum) otherwise:

.text:00005555555553DF      lea     rdx, [rax-1]    ; rdx=rax-1
.text:00005555555553E3      mov     ecx, eax
.text:00005555555553E5      and     ecx, 11b        ; ecx==0 <=> len(first_part_serial) is multiple of 4?
.text:00005555555553E8      cmp     rdx, 3          ; if edx<3 ...
.text:00005555555553EC      jnb     loc_5555555555D5 ; ...not jump, 
.text:00005555555553F2      mov     dl, 0AFh
.text:00005555555553F4      mov     bl, 56h ; 'V'
.text:00005555555553F6      xor     esi, esi        ; esi=0
.text:00005555555553F8      jmp     loc_555555555601
```

check if first_part_serial is len enough, if muliple of 4, assign an initial value to dl and bl, make esi=0 and then start computing a value (consider it a checksum):

```
.text:0000555555555601      test    rcx, rcx        ; if ecx==0 (multiple of 4) then skip this block ...
.text:0000555555555604      jz      short loc_55555555561E ; ... jmp
.text:0000555555555606      lea     rax, [rsp+rsi+58h+stripserial] ; padding with '0'
.text:000055555555560A      add     rax, 30h ; '0'
.text:000055555555560E      xor     esi, esi
.text:0000555555555610
.text:0000555555555610     loc_555555555610:   
.text:0000555555555610      add     dl, [rax+rsi]
.text:0000555555555613      add     bl, dl
.text:0000555555555615      add     rsi, 1
.text:0000555555555619      cmp     rcx, rsi
.text:000055555555561C      jnz     short loc_555555555610 ; end padding
.text:000055555555561E
.text:000055555555561E     loc_55555555561E:    ; compute checksum
.text:000055555555561E      movzx   eax, bl
.text:0000555555555621      shl     eax, 8
.text:0000555555555624      movsx   ecx, dl         ; increment o decrement edi esi automatically
.text:0000555555555627      add     ecx, eax
.text:0000555555555629      movzx   ecx, cx         ; end checksum
```

it is clear from code, but just to summarize: if needed consider remaining chars like 0 and make some math then compute the checksum

```
.text:000055555555562C      lea     rdx, format     ; "%04x"
.text:0000555555555633      lea     rbx, [rsp+58h+s2]
.text:0000555555555638      mov     esi, 5          ; maxlen
.text:000055555555563D      mov     rdi, rbx        ; s
.text:0000555555555640      xor     eax, eax
.text:0000555555555642      call    _snprintf       ; rcx what print, rdx format, esi maxlen, rdi destination
.text:0000555555555647      lea     rdi, [rsp+58h+last_part_serial] ; 
.text:000055555555564C      mov     rsi, rbx        ; 
.text:000055555555564F      call    _strcmp         ; compare the checksum with last_part_serial as string
.text:0000555555555654      test    eax, eax        ; if equal then....
.text:0000555555555656      setz    al              ; ....al=1 and function return OK
.text:0000555555555659
.text:0000555555555659     loc_555555555659:                       ; CODE XREF: pkv_check_checksum+1B↑j
.text:0000555555555659      add     rsp, 48h
.text:000055555555565D      pop     rbx
.text:000055555555565E      pop     r14
.text:0000555555555660      retn
```

a brief restatement in high level language of the checksum algo could be something like (without any check, no substring, no return of substring without '-', accpeting only 24 len serial, and so on):

```
def skeleton_compute_hash(in_serial):
    len_serial = len(in_serial)
    dl = 0xAF
    bl = 0x56
    for ii in range(0, len_serial, 4):  
        dl = (dl + ord(in_serial[ii])) & 0xFF
        bl = (bl + dl) & 0xFF
        dl = (dl + ord(in_serial[ii+1])) & 0xFF
        bl = ( bl + dl ) & 0xFF
        dl = ( dl + ord(in_serial[ii+2])  & 0xFF)
        bl = ( bl + dl ) & 0xFF
        dl = ( dl + ord(in_serial[ii+3]) ) & 0xFF
        bl = ( bl + dl ) & 0xFF
    eax = bl << 8
    if ((dl & (0x1<<7)) >> 7) == 0x1:
        ecx = dl + 0xFFFFFF00   
    else:
        ecx = dl

    ecx = (eax + ecx) & 0xFFFF
    ecx = "{:04X}".format(ecx)
    return ecx.lower() # i prefer lowercase since in this case doesn't matter
```

so in fact function, take two parameters, rdi=serial, rsi=a pointer to a var that will be filled by the function with the stripped serial, in the following code I will call it out_serial. Perform a checksum computed on the 0x10 char of the strippedserial and compare it as string with substring extracted from strippedserial between 0x11 and 0x14 char. This suggest that char from 0x11 and 0x14 should be [0-9a-f] because they should be the same of computed checksum

The interested reader could find details on all code and check performed by the function in the attached python script, it simulates the whole crackme

after the function return:

```
.text:0000555555555683       call    pkv_check_checksum
.text:0000555555555688       test    al, al          ; se eax==0 allora...
.text:000055555555568A       jz      error_exit ; ... jump to error_exit
.text:0000555555555690       mov     [rsp+68h+var_50], 0
.text:0000555555555695       mov     qword ptr [rsp+68h+nptr], 0
.text:000055555555569E       lea     rdi, [rsp+68h+out_serial] ; s
.text:00005555555556A3       call    _strlen
.text:00005555555556A8       cmp     rax, 8
.text:00005555555556AC       mov     ecx, 8
.text:00005555555556B1       cmovb   rcx, rax
.text:00005555555556B5       test    rcx, rcx
.text:00005555555556B8       jz      loc_555555555779

.text:0000555555555779       xor     ecx, ecx ; ecx=0
```

it compute the len, compare with zero and then jmp according and set ecx=0, read after for details

```
.text:00005555555556BE      mov     al, [rsp+68h+out_serial]
.text:00005555555556C2      test    al, al
.text:00005555555556C4      jz      loc_555555555779
.text:00005555555556CA      mov     [rsp+68h+nptr], al
.text:00005555555556CE      cmp     rcx, 1
.text:00005555555556D2      jz      loc_55555555577B
.text:00005555555556D8      mov     al, [rsp+68h+out_serial+1]
.text:00005555555556DC      test    al, al
.text:00005555555556DE      jz      loc_55555555593E
.text:00005555555556E4      mov     [rsp+68h+nptr+1], al
.text:00005555555556E8      cmp     rcx, 2
.text:00005555555556EC      jz      loc_55555555577B
.text:00005555555556F2      mov     al, [rsp+68h+out_serial+2]
.text:00005555555556F6      test    al, al
.text:00005555555556F8      jz      loc_555555555948
.text:00005555555556FE      mov     [rsp+68h+nptr+2], al
.text:0000555555555702      cmp     rcx, 3
.text:0000555555555706      jz      short loc_55555555577B
.text:0000555555555708      mov     al, [rsp+68h+out_serial+3]
.text:000055555555570C      test    al, al
.text:000055555555570E      jz      loc_555555555952
.text:0000555555555714      mov     [rsp+68h+nptr+3], al
.text:0000555555555718      cmp     rcx, 4
.text:000055555555571C      jz      short loc_55555555577B
.text:000055555555571E      mov     al, [rsp+68h+out_serial+4]
.text:0000555555555722      test    al, al
.text:0000555555555724      jz      loc_55555555595C
.text:000055555555572A      mov     [rsp+68h+nptr+4], al
.text:000055555555572E      cmp     rcx, 5
.text:0000555555555732      jz      short loc_55555555577B
.text:0000555555555734      mov     al, [rsp+68h+out_serial+5]
.text:0000555555555738      test    al, al
.text:000055555555573A      jz      loc_555555555966
.text:0000555555555740      mov     [rsp+68h+nptr+5], al
.text:0000555555555744      cmp     rcx, 6
.text:0000555555555748      jz      short loc_55555555577B
.text:000055555555574A      mov     al, [rsp+68h+out_serial+6]
.text:000055555555574E      test    al, al
.text:0000555555555750      jz      loc_555555555970
.text:0000555555555756      mov     [rsp+68h+nptr+6], al
.text:000055555555575A      cmp     rcx, 7
.text:000055555555575E      jz      short loc_55555555577B
.text:0000555555555760      mov     al, [rsp+68h+out_serial+7]
.text:0000555555555764      test    al, al
.text:0000555555555766      jz      loc_55555555597A
.text:000055555555576C      mov     [rsp+68h+nptr+7], al
.text:0000555555555770      jmp     short loc_55555555577B
```

so it is extracting ascii value from out_serial from 0 to 7 position and placing in nptr. in case of null then stop the copy and land directly at 

```
.text:000055555555577B      mov     eax, ecx
.text:000055555555577D      mov     [rsp+rax+68h+nptr], 0 ; add terminator in the middle of the serial
.text:0000555555555782      lea     rdi, [rsp+68h+nptr] ; nptr, contains the first 8 chars of serial
.text:0000555555555787      xor     esi, esi        ; endptr
.text:0000555555555789      mov     edx, 10h        ; base
.text:000055555555578E      call    _strtoll        ; print over a variable, the serial in hexadecimal
.text:0000555555555793      mov     r12, rax        ; store it on r12
```

the precedent code that jumped to the xor ecx, ecx land exactly at the same point, so the difference is in the ecx value. if out_serial has zero length than ecx=0 otherwise it contains the len 
the first part print 8 char of out_serial on a string in hexadecimal, this suggest exactly as the comparison for the checksum that character from 0 to 7 should be [0-9a-f]. result is stored on r12

```
.text:0000555555555796      xor     edi, edi        ; timer
.text:0000555555555798      call    _time
.text:000055555555579D      mov     edi, eax        ; seed
.text:000055555555579F      call    _srand
.text:00005555555557A4      call    _rand
.text:00005555555557A9      cdqe
.text:00005555555557AB      imul    rcx, rax, 2AAAAAABh 
.text:00005555555557B2      mov     rdx, rcx     
.text:00005555555557B5      shr     rdx, 63       
.text:00005555555557B9      shr     rcx, 32        
.text:00005555555557BD      add     ecx, edx        
.text:00005555555557BF      add     ecx, ecx        
.text:00005555555557C1      lea     ecx, [rcx+rcx*2] 
.text:00005555555557C4      sub     eax, ecx        
.text:00005555555557C6      cdqe
```

compute time, then _srand and after all rand, the result is stored in rax. the following lines of code are a common way that gcc implements to compute the remaining of a division, in this case the remaining of  divison by 6. More or less the idea is to define a number that divided by 2**32 is ~ 1/6 (slightly less to be clear). 
1/6 * 2**32 = 715827882.6666666 , round at 715827883 and in hex become 0x2aaaaaab. During the code, of course only the integer part is maintained and the remaining is discarded because numbers are not saved on float registers difference between numbers give a good way to compute the %6

```
.text:00005555555557C8      lea     rcx, key_check_pairs
.text:00005555555557CF      movzx   r14d, byte ptr [rax+rcx]
.text:00005555555557D4      mov     bpl, 1          ; bpl=1
.text:00005555555557D7      xor     r15d, r15d      ; r15d=0
.text:00005555555557DA      jmp     short loc_555555555843
```

and

```
.rodata:0000555555556004     key_check_pairs db 3, 5, 9, 6, 0Ah, 0Ch, 0, 0, 0, 0, 0, 0; 
```

considering that rax could assume value between [0,5] this means that r14d will be 3, 5, 9, 6, 0Ah or 0Ch. Set bpl=0 if r15>=3 (it will be important in the after but for now bpl will remain one in all other place so here is the only point in which can change value), make rd15d=0 and then jump and start the real check

```
.text:00005555555557E0     loc_5555555557E0:                       ; CODE XREF: pkv_check_key+29E↓j
.text:00005555555557E0 068                 mov     ecx, eax
.text:00005555555557E2 068                 sar     edi, cl         ; temp_val[11]
.text:00005555555557E4 068                 and     edx, edi        ; tmep_val[12]
.text:00005555555557E6 068                 xor     edx, esi        ; temp_val[13]
.text:00005555555557E8 068                 mov     edi, edx
.text:00005555555557EA
.text:00005555555557EA     loc_5555555557EA:                       ; CODE XREF: pkv_check_key+2B0↓j
.text:00005555555557EA 068                 mov     [rsp+68h+var_4A], 0 ; add terminatore a s1
.text:00005555555557EF 068                 mov     word ptr [rsp+68h+s1], 0 ; cancella il vecchio s1 ????
.text:00005555555557F6 068                 movzx   ecx, dil
.text:00005555555557FA 068                 mov     esi, 3          ; maxlen
.text:00005555555557FF 068                 lea     rbx, [rsp+68h+s1]
.text:0000555555555804 068                 mov     rdi, rbx        ; s
.text:0000555555555807 068                 lea     rdx, asc_555555556060 ; "%x"
.text:000055555555580E 068                 xor     eax, eax
.text:0000555555555810 068                 call    _snprintf       
.text:0000555555555815 068                 mov     rdi, rbx        ; s1
.text:0000555555555818 068                 lea     rsi, [rsp+68h+s2] ; s2
.text:000055555555581D 068                 call    _strcmp
.text:0000555555555822 068                 test    eax, eax
.text:0000555555555824 068                 jnz     loc_555555555925
.text:000055555555582A
.text:000055555555582A     loc_miniloop:                       
.text:000055555555582A 068                 cmp     r15, 3
.text:000055555555582E 068                 lea     rax, [r15+1]
.text:0000555555555832 068                 setb    bpl             ; bpl=1 if CF=1
.text:0000555555555836 068                 mov     r15, rax
.text:0000555555555839 068                 cmp     rax, 4
.text:000055555555583D 068                 jz      loc_555555555925 
.text:0000555555555843
.text:0000555555555843     loc_555555555843:                       ; <---- LAND HERE
.text:0000555555555843 068                 bt      r14d, r15d      ; extract bit 0,1,2,3 from r14d until 1 found
.text:0000555555555843                                             ; r14=3, 5, 9, 6, 0Ah, 0Ch => r15=0 0 0 1 1 2
.text:0000555555555847 068                 jnb     short loc_miniloop
.text:0000555555555849 068                 mov     [rsp+68h+var_5A], 0
.text:000055555555584E 068                 mov     word ptr [rsp+68h+s2], 0
.text:0000555555555855 068                 lea     rax, lookup_tbl1
.text:000055555555585C 068                 mov     r13d, [rax+r15*4] ; used to define string start
.text:0000555555555860 068                 lea     rax, lookup_tbl2
.text:0000555555555867 068                 movsxd  rbx, dword ptr [rax+r15*4] ; used to define string length
.text:000055555555586B 068                 lea     rdi, [rsp+68h+out_serial] ; s
.text:0000555555555870 068                 call    _strlen
.text:0000555555555875 068                 xor     ecx, ecx        ; ecx=0
.text:0000555555555877 068                 test    r13d, r13d      
.text:000055555555587A 068                 cmovs   r13d, ecx       
.text:000055555555587E 068                 cmp     rax, rbx       
.text:0000555555555881 068                 cmovnb  eax, ebx        
.text:0000555555555884 068                 sub     eax, r13d      
.text:0000555555555887 068                 jle     short loc_5555555558B7 
.text:0000555555555889 068                 mov     ecx, r13d
.text:000055555555588C 068                 lea     rdx, [rsp+rcx+68h+var_68]
.text:0000555555555890 068                 add     rdx, 20h ; ' '  
.text:0000555555555894 068                 xor     ecx, ecx        
.text:0000555555555896 068                 nop     word ptr [rax+rax+00000000h]
.text:00005555555558A0
.text:00005555555558A0     loop_build_s2:                          ; CODE XREF: pkv_check_key+243↓j
.text:00005555555558A0 068                 movzx   ebx, byte ptr [rdx+rcx] 
.text:00005555555558A4 068                 test    bl, bl
.text:00005555555558A6 068                 jz      short loc_5555555558B7
.text:00005555555558A8 068                 mov     [rsp+rcx+68h+s2], bl
.text:00005555555558AC 068                 add     rcx, 1
.text:00005555555558B0 068                 cmp     rax, rcx        
.text:00005555555558B3 068                 jnz     short loop_build_s2 
.text:00005555555558B5 068                 mov     ecx, eax
.text:00005555555558B7
.text:00005555555558B7     loc_5555555558B7:                       ; CODE XREF: pkv_check_key+217↑j
.text:00005555555558B7                                             ; pkv_check_key+236↑j
.text:00005555555558B7 068                 mov     eax, ecx
.text:00005555555558B9 068                 mov     [rsp+rax+68h+s2], 0 ; add terminatore
.text:00005555555558BE 068                 lea     rax, lookup_tbl3 
.text:00005555555558C5 068                 movzx   ecx, byte ptr [rax+r15*4]
.text:00005555555558CA 068                 lea     rax, lookup_tbl4
.text:00005555555558D1 068                 movzx   eax, byte ptr [rax+r15*4]
.text:00005555555558D6 068                 lea     rdx, lookup_tbl5
.text:00005555555558DD 068                 movzx   edx, byte ptr [rdx+r15*4]
.text:00005555555558E2 068                 lea     esi, [rcx+rcx*4]
.text:00005555555558E5 068                 lea     esi, [rcx+rsi*8] ; temp_val[2]
.text:00005555555558E8 068                 shr     esi, 0Ah
.text:00005555555558EB 068                 lea     esi, [rsi+rsi*4]
.text:00005555555558EE 068                 lea     esi, [rsi+rsi*4]
.text:00005555555558F1 068                 sub     cl, sil         ; temp_val[5]
.text:00005555555558F4 068                 imul    esi, eax, 0ABh  ; temp_val[6]
.text:00005555555558FA 068                 shr     esi, 9          ; temp_val[7]
.text:00005555555558FD 068                 lea     esi, [rsi+rsi*2] ; temp_val[8]
.text:0000555555555900 068                 sub     al, sil         ; temp_val[9]
.text:0000555555555903 068                 mov     esi, r12d
.text:0000555555555906 068                 sar     esi, cl         ; temp_val[10]
.text:0000555555555908 068                 mov     edi, r12d
.text:000055555555590B 068                 test    cl, 1
.text:000055555555590E 068                 jnz     loc_5555555557E0
.text:0000555555555914 068                 mov     ecx, eax        ; case not jumped
.text:0000555555555916 068                 sar     edi, cl         ; temp_val[11]
.text:0000555555555918 068                 movzx   eax, sil
.text:000055555555591C 068                 or      edi, edx        ; temp_val[12]
.text:000055555555591E 068                 xor     edi, eax        ; temp_val[13]
.text:0000555555555920 068                 jmp     loc_5555555557EA
```

in particular 

```
.text:000055555555582A     loc_miniloop:
.text:000055555555582A      cmp     r15, 3
.text:000055555555582E      lea     rax, [r15+1]
.text:0000555555555832      setb    bpl             ; bpl=1 if CF=1
.text:0000555555555836      mov     r15, rax
.text:0000555555555839      cmp     rax, 4
.text:000055555555583D      jz      loc_555555555925 ; if bpl==0 (r15>=3) and eax==4 then it will jump
.text:0000555555555843
.text:0000555555555843     loc_555555555843:                       ; <---- LAND HERE
.text:0000555555555843      bt      r14d, r15d      
.text:0000555555555847      jnb     short loc_miniloop
```

it lands on what I called miniloop, r14d as already observed could assume 3, 5, 9, 6, 0Ah or 0Ch and r15d at the beginning is zero but it will be increase with "lea rax, [r15+1]" and "mov r15, rax"
this loop keep going until it found 1 in r14d in the position of r15d. if r14 is 3 then in the next iteration it will be equal to 4 and then it will jump to loc_555555555925
In binary 0x3,5,9,6,a,c are

```
>>> bin(0x3) '0b11'
>>> bin(0x5) '0b101'
>>> bin(0x9) '0b1001'
>>> bin(0x6) '0b110'
>>> bin(0xa) '0b1010'
>>> bin(0xc) '0b1100'
```

This is equivalent to say that bt will set flag and exit from miniloop in following cases:

```
r14d	0x3 -   '0b11'	-> r15d=0
r14d	0x5 -  '0b101'	-> r15d=0
r14d	0x9 - '0b1001'	-> r15d=0
r14d	0x6 -  '0b110'	-> r15d=1
r14d	0xa - '0b1010'	-> r15d=1
r14d	0xc - '0b1100'	-> r15d=2
```

These informations could be refilled in the following schema:

```
rand	0	1	2	3	4	5
r14d	3	5	9	6	0xa	0xc
r15d	0	0	0	1	1	2
```

then if for some reason rax==4 it will jmp to

```
.text:0000555555555925     loc_555555555925:                      
.text:0000555555555925      xor     bpl, 1          ; if bpl=0, xor bpl,1 => bpl=1
.text:0000555555555929
.text:0000555555555929     loc_555555555929:                       
.text:0000555555555929      and     bpl, 1          ; 1 and 1 => bpl=1
.text:000055555555592D      mov     eax, ebp        ; eax = ebp (eax!=0 good!)
.text:000055555555592F      add     rsp, 38h
.text:0000555555555933      pop     rbx
.text:0000555555555934      pop     r12
.text:0000555555555936      pop     r13
.text:0000555555555938      pop     r14
.text:000055555555593A      pop     r15
.text:000055555555593C      pop     rbp
.text:000055555555593D      retn
```

considering that if function return with a value different from zero the crackme is solved than if it land at the xor bpl, 1 AND bpl is zero it will become 1, the following "and bpl,1" is 1 and eax=1!

```
.text:0000555555555849 068                 mov     [rsp+68h+var_5A], 0
.text:000055555555584E 068                 mov     word ptr [rsp+68h+s2], 0
.text:0000555555555855 068                 lea     rax, lookup_tbl1
.text:000055555555585C 068                 mov     r13d, [rax+r15*4] ; used to define string start
.text:0000555555555860 068                 lea     rax, lookup_tbl2
.text:0000555555555867 068                 movsxd  rbx, dword ptr [rax+r15*4] ; used to define string length
.text:000055555555586B 068                 lea     rdi, [rsp+68h+out_serial] ; s
.text:0000555555555870 068                 call    _strlen
.text:0000555555555875 068                 xor     ecx, ecx        ; ecx=0
.text:0000555555555877 068                 test    r13d, r13d      ; if r13d == 0 ...
.text:000055555555587A 068                 cmovs   r13d, ecx       ; ... r13d = ecx = 0
.text:000055555555587E 068                 cmp     rax, rbx        ; if shorten the requested
.text:0000555555555881 068                 cmovnb  eax, ebx        ; ...then eax=requested
.text:0000555555555884 068                 sub     eax, r13d       ; always 2 
.text:0000555555555887 068                 jle     short loc_5555555558B7 ; ... not jump if len enough
.text:0000555555555889 068                 mov     ecx, r13d
.text:000055555555588C 068                 lea     rdx, [rsp+rcx+68h+var_68]
.text:0000555555555890 068                 add     rdx, 20h ; ' '  ; rdx==out_serial from k char, k-position could be [8 a c e]
.text:0000555555555894 068                 xor     ecx, ecx        ; ecx=0
.text:0000555555555896 068                 nop     word ptr [rax+rax+00000000h]
```

first of all it set to zero two vars, then it loads two lookup tables and use r15 as index. The interesting thing is the difference between two values with the same index from the two lookup tables will be always 2. It compute the len(out_serial). "lea     rdx, [rsp+rcx+68h+var_68]" is a pointer to the rcx char of out_serial. rcx in this case is the result from lookup table. So the first lookup table simply tell from with chars extract, the second lookup tables point to the last char of substring. As already state, the number of chars is two, so extract two char starting from different point, in this case from position 8, a, c, or e (iff r15d 0, 1, 2 or 3)

```
.text:00005555555558A0     loop_build_s2:                          
.text:00005555555558A0       movzx   ebx, byte ptr [rdx+rcx] ; rcx counter, rdx point inside out_serial
.text:00005555555558A4       test    bl, bl
.text:00005555555558A6       jz      short loc_5555555558B7
.text:00005555555558A8       mov     [rsp+rcx+68h+s2], bl
.text:00005555555558AC       add     rcx, 1
.text:00005555555558B0       cmp     rax, rcx        ; rax==2, loop has two iterations
.text:00005555555558B3       jnz     short loop_build_s2 ; loop 
.text:00005555555558B5       mov     ecx, eax
```

copy char from out_serial in s2, starting from position (decided before) for a total length of two iterations, and then save result on ecx

```
.text:00005555555558B7     loc_5555555558B7:           
.text:00005555555558B7 068                 mov     eax, ecx
.text:00005555555558B9 068                 mov     [rsp+rax+68h+s2], 0 ; add terminator
.text:00005555555558BE 068                 lea     rax, lookup_tbl3 ; 
.text:00005555555558C5 068                 movzx   ecx, byte ptr [rax+r15*4]
.text:00005555555558CA 068                 lea     rax, lookup_tbl4
.text:00005555555558D1 068                 movzx   eax, byte ptr [rax+r15*4]
.text:00005555555558D6 068                 lea     rdx, lookup_tbl5
.text:00005555555558DD 068                 movzx   edx, byte ptr [rdx+r15*4]
.text:00005555555558E2 068                 lea     esi, [rcx+rcx*4]
.text:00005555555558E5 068                 lea     esi, [rcx+rsi*8] ; temp_val[2]
.text:00005555555558E8 068                 shr     esi, 0Ah
.text:00005555555558EB 068                 lea     esi, [rsi+rsi*4]
.text:00005555555558EE 068                 lea     esi, [rsi+rsi*4]
.text:00005555555558F1 068                 sub     cl, sil         ; temp_val[5]
.text:00005555555558F4 068                 imul    esi, eax, 0ABh  ; temp_val[6]
.text:00005555555558FA 068                 shr     esi, 9          ; temp_val[7]
.text:00005555555558FD 068                 lea     esi, [rsi+rsi*2] ; temp_val[8]
.text:0000555555555900 068                 sub     al, sil         ; temp_val[9]
.text:0000555555555903 068                 mov     esi, r12d       ; r12d point to out_serial
.text:0000555555555906 068                 sar     esi, cl         ; temp_val[10]
.text:0000555555555908 068                 mov     edi, r12d
.text:000055555555590B 068                 test    cl, 1
.text:000055555555590E 068                 jnz     loc_5555555557E0
.text:0000555555555914 068                 mov     ecx, eax        
.text:0000555555555916 068                 sar     edi, cl         ; temp_val[11]
.text:0000555555555918 068                 movzx   eax, sil
.text:000055555555591C 068                 or      edi, edx        ; temp_val[12]
.text:000055555555591E 068                 xor     edi, eax        ; temp_val[13]
.text:0000555555555920 068                 jmp     loc_5555555557EA
```

it is a routine to ocmpute a checksum, read value from two lookup tables and then do some math. For the sake of clarity, here a brief code in python that mimic the computing

```
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

temp_val_esi = val_tbl4 * 0xAB # eax == 0 ???? perché ????
print("temp_val[6] è 0x%x" % temp_val_esi)

temp_val_esi = (temp_val_esi >> 0x9) & 0xffffffffffffffff
print("temp_val[7] è 0x%x" % temp_val_esi)

temp_val_esi = temp_val_esi * 3
print("temp_val[8] è 0x%x" % temp_val_esi)

temp_val_ax = val_tbl4 - temp_val_esi
print("temp_val[9] è 0x%x" % temp_val_ax)

temp_val_esi = ( r12 >> temp_val_cl )
print("temp_val[10] è 0x%x" % temp_val_esi)
```

```
.text:00005555555557E0        mov     ecx, eax
.text:00005555555557E2        sar     edi, cl         ; temp_val[11]
.text:00005555555557E4        and     edx, edi        ; temp_val[12]
.text:00005555555557E6        xor     edx, esi        ; temp_val[13]
.text:00005555555557E8        mov     edi, edx
.text:00005555555557EA
.text:00005555555557EA        mov     [rsp+68h+var_4A], 0 ; add terminator to s1
.text:00005555555557EF        mov     word ptr [rsp+68h+s1], 0 ; delete old s1, for the future
.text:00005555555557F6        movzx   ecx, dil
.text:00005555555557FA        mov     esi, 3          ; maxlen
.text:00005555555557FF        lea     rbx, [rsp+68h+s1]
.text:0000555555555804        mov     rdi, rbx        ; s
.text:0000555555555807        lea     rdx, asc_555555556060 ; "%x"
.text:000055555555580E        xor     eax, eax
.text:0000555555555810        call    _snprintf       ; rcx what to print, rdx in which format, esi maxlen, rdi where
.text:0000555555555815        mov     rdi, rbx        ; s1
.text:0000555555555818        lea     rsi, [rsp+68h+s2] ; s2
.text:000055555555581D        call    _strcmp
.text:0000555555555822        test    eax, eax
.text:0000555555555824        jnz     loc_555555555925
```

it keeps doing some math, print the result on a string and then compare substring s2 extracted before with the computed s1, if equals then do not jump. In case of jump, bpl is 1 so the program will return an error otherwise keep going to what I called miniloop

```
.text:000055555555582A     loc_miniloop:
.text:000055555555582A        cmp     r15, 3
.text:000055555555582E        lea     rax, [r15+1]
.text:0000555555555832        setb    bpl             ; bpl=1 if r15<3
.text:0000555555555836        mov     r15, rax
.text:0000555555555839        cmp     rax, 4
.text:000055555555583D        jz      loc_555555555925 ; if bpl==0 ( r15>=3) and eax==4 then end!
...
```

it will do exactly the same work done before but with an already incremented r15, and once r15 reach the value of three, then rax will be 4, bpl=0 and the jump will happen. So what really happens is a check is performed starting from a random position between 0 and 2 and for all greater position until 3. Consider tha position 0 appears tree times, 1 two times and 2 one time only, this means that there is a probability of 50% of starting from the beginning, 1/3=33% of starting from position 1 and 1/6 to start from position 2

The keygen.py generate a working serial starting from a fixed string, in my case is 12345678ea6d2688b68basdf. I added a lot of print with a string point to the commented code, just to help if anyone would need it

This complete the reversing, thanks to froglover22 for this crackme!

lewis ( bottonim at yahoo.it ) 06/21/2024
