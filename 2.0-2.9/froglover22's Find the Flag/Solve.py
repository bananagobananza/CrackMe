def hex_to_ascii(hex_string):
    ascii_string = bytes.fromhex(hex_string).decode('ascii')
    return ascii_string

# Example usage
Chunks = ["6A4627256A6D6660", "252476716477626B", "6F66206576756F59", "25606D7125616B70"]

for i in Chunks:
    ascii_string = hex_to_ascii(i)
    print(ascii_string[::-1])
print("")

def hex_to_ascii(hex_string):
    try:
        return bytearray.fromhex(hex_string)
    except ValueError:
        return bytearray(hex_string, 'ascii')

def safe_decode(byte_array):
    try:
        return byte_array.decode('ascii')[::-1]
    except UnicodeDecodeError:
        return byte_array.hex()[::-1]

Chunks = ["6A4627256A6D6660", "252476716477626B", "6F66206576756F59", "25606D7125616B70", "flag.\\"]

for i in range(len(Chunks)):
    Chunks[i] = hex_to_ascii(Chunks[i])

for i in range(len(Chunks)):
    for j in range(min(8, len(Chunks[i]))):
        Chunks[i][j] ^= 5
    print(safe_decode(Chunks[i]))

# echo "Co
# ngrats! 
# \jps`%cj
# und the 
# Y+bdic
