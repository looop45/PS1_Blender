#include <iostream>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <arpa/inet.h>
#include <string.h>

#include "json.hpp"
#include "CommandQueue.h"

using json = nlohmann::json;

const char* SOCKET_PATH = "/tmp/ps1_render";

class host
{
    public:
        host() {}

        int start_host();
        void stop_host();
        int connect_client();
        int handle_client(CommandQueue& command_queue);
    
    private:
        int server_sock;
        int client_sock;
        sockaddr_un addr;
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
    // Receive and send data
    char buffer[1024];
    while (true) {
        memset(buffer, 0, sizeof(buffer));
        int bytes_received = recv(client_sock, buffer, sizeof(buffer) - 1, 0);
        if (bytes_received <= 0) {
            std::cout << "Client disconnected\n";
            return 0;
        }
        std::cout << "Server end Received: " << buffer << "\n";

        // Echo data back to client
        json value = {
            {"draw_data", {1.0, 0.0, 0.0, 1.0}}
            };

        std::string data = value.dump();

        std::cout << "Server sending..." << data << std::endl;
        
        if (send(client_sock, data.c_str(), data.length(), 0) < 0)
        {
            std::cerr << "Send failed!" << std::endl;
            close(client_sock);
            return -1;
        }
    }
}


void host::stop_host()
{
    // Clean up
    close(client_sock);
    close(server_sock);

    return;
}

