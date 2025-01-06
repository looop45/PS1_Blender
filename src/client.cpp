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

    char buffer[BUFFER_SIZE];
    while (true) {
        // Receive scene data
        memset(buffer, 0, BUFFER_SIZE);
        int bytes_received = recv(sock, buffer, BUFFER_SIZE, 0);
        if (bytes_received <= 0) 
        {
            std::cout << "Server disconnected or error occurred.\n";
            break;
        }

        // Process received scene data (assuming a simple string here)
        std::string scene_data(buffer, bytes_received);
        std::cout << "Received scene data: " << scene_data << std::endl;

        // Prepare pixel data to send back
        int pixel_values[] = {255, 128, 64};  // Example pixel values
        char pixel_buffer[sizeof(pixel_values)];
        memcpy(pixel_buffer, pixel_values, sizeof(pixel_values));

        // Send pixel data
        int bytes_sent = send(sock, pixel_buffer, sizeof(pixel_buffer), 0);
        if (bytes_sent <= 0) {
            std::cerr << "Failed to send pixel data.\n";
            break;
        }
        std::cout << "Sent pixel data back to server.\n";
    }

    // Close socket
    close(sock);
}
