#include <iostream>
#include <cstring>  // For memset and memcpy
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>  // For close()

#define BUFFER_SIZE 4096

void client() {
    int sock = 0;
    struct sockaddr_in server_address;

    // Create socket
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        std::cerr << "Socket creation error.\n";
        return;
    }

    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(6969);

    // Convert IPv4 address from text to binary
    if (inet_pton(AF_INET, "127.0.0.1", &server_address.sin_addr) <= 0) {
        std::cerr << "Invalid address or address not supported.\n";
        return;
    }

    // Connect to server
    if (connect(sock, (struct sockaddr*)&server_address, sizeof(server_address)) < 0) {
        std::cerr << "Connection failed.\n";
        return;
    }

    std::cout << "Connected to server.\n";

    // Receive the test string
    char buffer[BUFFER_SIZE] = {0};
    int bytes_received = recv(sock, buffer, BUFFER_SIZE, 0);
    if (bytes_received > 0) {
        std::string received_message(buffer, bytes_received);
        std::cout << "Received from server: " << received_message << std::endl;

        // Optionally send an acknowledgment back
        std::string ack_message = "Hello from C++ Client!";
        send(sock, ack_message.c_str(), ack_message.size(), 0);
        std::cout << "Sent acknowledgment to server.\n";
    } else {
        std::cerr << "Failed to receive data from server.\n";
    }

    // Close socket
    close(sock);
}