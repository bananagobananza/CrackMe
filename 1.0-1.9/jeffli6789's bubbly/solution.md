# Crackme Report for jeffli6789's bubbly
**Solution by 7cherubin**

## Crackme Information

- Crackme ID: 5f00a02533c5d4285070947a

## Summary

The program contains an array literal of 20 integers between 0 and 19 in scrumbled order.

The users input is used to swap the integers at the indexes:
* UserInput
* UserInput + 1

The program uses XOR to make the swapping faster than loading and unloading the numbers from memory.

For the program to succeed, the sequence of 20 integers must be sorted in ascending order.

*In essence, it implements bubble sort with the decision making being done by the user.*

The correct sequence of numbers to input is:
```bash
2
1
0
3
5
4
7
9
10
13
12
11
15
14
17
16
15
18
17
16
15
```

## Tools Used

- DIE Engine - https://github.com/horsicq/DIE-engine
- GDB - https://sourceware.org/gdb/

## Notes

Python code to generate solution:

```python

sequence = [1, 2, 6, 0, 3, 5, 4, 8, 7, 12, 9, 10, 13, 17, 11, 18, 14, 19, 16, 15]

index = 1

while index < len(sequence):
    if(index < len(sequence) - 1 and sequence[index] > sequence[index+1]):
        temp = sequence[index]
        sequence[index] = sequence[index+1]
        sequence[index+1] = temp
        print(index)
        index = 0
    else:
        index += 1
        
print(sequence)

```