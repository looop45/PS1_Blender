#pragma once
#include <iostream>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <arpa/inet.h>
#include <string.h>
#include <cstring>
#include <cstdint>

#include "PixelBuffer.h"
#include "CommandQueue.h"
#include "Messages.h"
#include "DrawCommand.h"

const char* SOCKET_PATH = "/tmp/ps1_render";

class host
{
    public:
        host() {}

        int start_host();
        void stop_host();
        int connect_client();
        int handle_client(CommandQueue& command_queue);
        int send_message(ServerMessage type, const std::vector<float>& data);
    
    private:
        int server_sock;
        int client_sock;
        sockaddr_un addr;

        ClientMessage recv_message(std::string& data);
        std::shared_ptr<Command> parse_message(const ClientMessage message_type, std::string& message);
};

int host::start_host()
{
    unlink(SOCKET_PATH);

    // Create a UNIX domain socket
    server_sock = socket(AF_UNIX, SOCK_STREAM, 0);
    if (server_sock < 0) {
        std::cerr << "Error creating socket\n";
        return 1;
    }

    // Set up the socket address structure
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path) - 1);

    // Bind the socket to the file path
    if (bind(server_sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        std::cerr << "Error binding socket\n";
        close(server_sock);
        return 1;
    }

    // Start listening for connections
    if (listen(server_sock, 5) < 0) {
        std::cerr << "Failed to listen\n";
        close(server_sock);
        return 1;
    }

    std::cout << "Server listening on port " << SOCKET_PATH << "...\n";

    return server_sock;
}

int host::connect_client()
{
    // Accept a client connection
    sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);
    client_sock = accept(server_sock, (struct sockaddr*)&client_addr, &client_len);
    if (client_sock < 0) {
        std::cerr << "Failed to accept client\n";
        close(server_sock);
        return 1;
    }

    std::cout << "Client connected\n";

    return client_sock;
}

int host::handle_client(CommandQueue& command_queue)
{
    std::string data;
    ClientMessage type = recv_message(data);
    std::shared_ptr<Command> command = parse_message(type, data);
    command_queue.push(command);
    return 1;
}


void host::stop_host()
{
    // Clean up
    close(client_sock);
    close(server_sock);

    return;
}

ClientMessage host::recv_message(std::string& data)
{
    // Read the header first
    Header header;
    ssize_t bytes_received = recv(client_sock, &header, sizeof(header), MSG_WAITALL);
    if (bytes_received < sizeof(header)) {
        perror("recv header");
        close(client_sock);
    }

    //std::cout << "Message Size: " << header.message_size << "\n";
    //std::cout << "Message Type: " << static_cast<int>(header.message_type) << "\n";

    // Allocate buffer for the message data
    std::vector<unsigned char> message_data(header.message_size);
    bytes_received = recv(client_sock, message_data.data(), header.message_size, MSG_WAITALL);
    if (bytes_received < static_cast<ssize_t>(header.message_size)) {
        perror("recv data");
        close(client_sock);
    }

    // Interpret message based on type
    std::string message_string(message_data.begin(), message_data.end());
    data = message_string;

    return ClientMessage(header.message_type);
}

std::shared_ptr<Command> host::parse_message(const ClientMessage message_type, std::string& message_data)
{
    std::shared_ptr<Command> command;

    switch (message_type)
    {
    case ClientMessage::Start:
        /* code */
        break;
    case ClientMessage::Stop:
        /* code */
        break;
    case ClientMessage::Update:
        /* code */
        break;
    case ClientMessage::Draw:
        uint16_t width, height;
        std::memcpy(&width, message_data.data(), 2);
        std::memcpy(&height, message_data.data() + 2, 2);
        //TODO: Add camera data
        command = std::make_shared<DrawCommand>(width, height);
        break;
    
    default:
        perror("Invalid Command!");
        break;
    }
    return command;
}

int host::send_message(ServerMessage type, const std::vector<float>& data)
{
    uint8_t msgType = static_cast<uint8_t>(type);
    uint32_t sizeBytes = data.size() * sizeof(float);

    if (sizeBytes == 0) {
        std::cout << "Data is empty!!!" << std::endl;
        return 1;
    }

    Header header{sizeBytes, msgType};

    // Serialize the header and data
    std::vector<uint8_t> packet(sizeof(Header) + sizeBytes);
    std::memcpy(packet.data(), &header, sizeof(header));
    std::memcpy(packet.data() + sizeof(Header), data.data(), sizeBytes);

    ssize_t sentBytes = 0;
    while (sentBytes < static_cast<ssize_t>(packet.size())) {
        ssize_t result = send(client_sock, packet.data() + sentBytes, packet.size() - sentBytes, 0);
        if (result < 0) {
            perror("Failed to send data");
            return 1;
        }
        sentBytes += result;
    }

    return 0;
}