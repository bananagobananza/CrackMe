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
