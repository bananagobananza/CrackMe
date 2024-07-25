File Check:

```
➜  level1 file level1
level1: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=89f40555f67806b4082e5785d91836bb6baaaa9d, for GNU/Linux 3.2.0, not stripped
➜  level1 checksec level1
[*] '/home/mark/Desktop/RevEngr/CrackMes/level1/level1'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
➜  level1 
```

### Static Analysis

I decompiled the binary using IDA 

Here's the main function pseudo code

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  char v4[64]; // [rsp+10h] [rbp-40h] BYREF

  printf("Welcome to Easy Crack Me");
  printf("What is the Secret ?");
  __isoc99_scanf("%64s", v4);
  if ( (unsigned int)checkPass(v4) )
    printf("You are correct :)");
  else
    printf("Better luck next time. :(");
  return 0;
}
```

It receives our input then use it as a parameter to the *checkPass* function

Here's the pseudo code

```c
__int64 __fastcall checkPass(_BYTE *a1)
{
  __int64 result; // rax

  if ( *a1 != 's' )
    return 0LL;
  result = (unsigned __int8)a1[1];
  if ( (_BYTE)result == 'u' )
  {
    result = (unsigned __int8)a1[2];
    if ( (_BYTE)result == 'd' )
    {
      result = (unsigned __int8)a1[3];
      if ( (_BYTE)result == 'o' )
      {
        result = (unsigned __int8)a1[4];
        if ( (_BYTE)result == '0' )
        {
          result = (unsigned __int8)a1[5];
          if ( (_BYTE)result == 'x' )
          {
            result = (unsigned __int8)a1[6];
            if ( (_BYTE)result == '1' )
            {
              result = (unsigned __int8)a1[7];
              if ( (_BYTE)result == '8' )
                return 1LL;
            }
          }
        }
      }
    }
  }
  return result;
}
```

From the we can conclude that:
- The 0th indexed character must be *s*
- The first indexed character must be *u*
- The second indexed character must be *d*
- The fourth indexed character must be *o*
- The fifth indexed character must be *0*
- The sixth indexed character must be *x*
- The seventh indexed character must be *1*
- The eight indexed character must be *8*

Which makes the final password to be *sudo0x18*

Trying it works


```
➜  level1 ./level1 
Welcome to Easy Crack MeWhat is the Secret ? sudo0x18
You are correct :)
```

And that's all 👻
