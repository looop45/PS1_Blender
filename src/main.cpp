#include <iostream>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

#include "CommandQueue.h"
#include "Scene.h"
#include "host.h"
#include "Engine.h"

// Global variables
std::atomic<bool> running(true);
Scene shared_scene;
std::mutex scene_mtx;

void server_thread(CommandQueue& command_queue, DrawData& pixel_buffer)
{
    host render_host;
    render_host.start_host();
    render_host.connect_client();

    while (running) 
    {
        if (render_host.handle_client(command_queue, pixel_buffer) == 0)
        {
            running = false;
            break;
        }
    }

    render_host.stop_host();
}

int render_loop(CommandQueue& command_queue, DrawData& drawData) 
{
    Engine engine;

    while (running) 
    {
        json cmd;
        if (command_queue.pop(cmd)) {
            // Process draw command
            std::cout << "Processing command: " << cmd["cmd"] << std::endl;

            // Perform rendering based on the command
            std::vector<uint8_t> pixels = engine.handleCommand(cmd);
            drawData.write(pixels);
            
        }

        /*// Optionally update rendering based on the scene
        {
            std::lock_guard<std::mutex> lock(scene_mtx);
            // Use shared_scene for rendering
        }*/

        // Perform rendering (e.g., OpenGL draw calls).*/
    }

    return 0;
}

int main()
{
    CommandQueue command_queue;
    DrawData drawData;

    std::thread server(server_thread, std::ref(command_queue), std::ref(drawData));

    render_loop(command_queue, drawData);

    server.join();

    return 0;
}