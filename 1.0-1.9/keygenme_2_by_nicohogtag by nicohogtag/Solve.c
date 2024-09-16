#include <stdio.h>
#include <string.h>

int calculate_serial(const char *username) {
    int v8 = 0;
    int v7 = 0x80899;

    // Sum up to the first 10 characters of the username
    for (int i = 0; i < strlen(username) && i < 10; i++) {
        v8 += (int)username[i];
        v7 += v8;
    }

    // Break down the calculation of v6 into separate steps
    int sum_v8_v7 = v8 + v7;
    int term1 = 7 * sum_v8_v7;
    int term2 = -v8;
    int term3 = 13 * (v7 / 2);
    int intermediate = term1 + term2 + term3;
    int v6 = intermediate * 7 * sum_v8_v7;

    if (v6 < 0) {
        v6 = -v6;
    }

    return v6;
}

int main() {
    char username[256];
    printf("Enter your username: ");
    fgets(username, sizeof(username), stdin);

    // Remove newline character if present
    size_t len = strlen(username);
    if (len > 0 && username[len - 1] == '\n') {
        username[len - 1] = '\0';
        len--;  // Adjust length after removing newline
    }

    printf("Length of input: %zu\n", len);

    int serial = calculate_serial(username);
    printf("Generated serial: %d\n", serial);

    return 0;
}
