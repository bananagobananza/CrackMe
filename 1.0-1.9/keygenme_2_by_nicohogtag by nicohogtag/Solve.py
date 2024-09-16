def calculate_serial(username):
    v8 = 0
    v7 = 0x80899

    # Sum up to the first 10 characters of the username
    for i in range(min(len(username), 10)):
        v8 += ord(username[i])
        v7 += v8

    v6 = (7 * (v8 + v7) - v8 + 13 * (v7 // 2)) * 7 * (v8 + v7)
    if v6 < 0:
        v6 = -v6

    return v6 & 0xFFFFFFFF

def main():
    username = input("Enter your username: ")
    serial = calculate_serial(username)
    print(f"Generated serial: {serial}")

if __name__ == "__main__":
    main()
