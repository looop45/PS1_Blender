#include <iostream>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <chrono>
#include <iomanip>
#include <fstream>

#include "CommandQueue.h"
#include "Scene.h"
#include "host.h"
#include "Engine.h"

// Global variables
std::atomic<bool> running(true);
Scene shared_scene;
std::mutex scene_mtx;

std::atomic<bool> debugger_attached(false);
std::condition_variable debugger_cv;
std::mutex debugger_mtx;

void recv_thread(host& render_host, CommandQueue& command_queue)
{
    while (running) 
    {
        if (render_host.handle_client(command_queue) == 0)
        {
            running = false;
            break;
        }
    }
}

void send_thread(host& render_host, std::shared_ptr<PixelBuffer> pixel_buffer)
{
    while (running)
    {
        std::vector<float> out_data;

        if (pixel_buffer->read(out_data))
        {
            render_host.send_message(ServerMessage::Result, out_data);
        }
    }
}

int render_loop(CommandQueue& command_queue, std::shared_ptr<PixelBuffer> pixelBuffer) 
{
    Engine engine(pixelBuffer);
    std::cout << "Server: Render loop running. Engine started." << std::endl;


    while (running) 
    {
        std::shared_ptr<Command> cmd;
        if (command_queue.pop(cmd)) {
            // Perform command
            cmd->execute( engine ); 
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

void server_init(CommandQueue& command_queue, std::shared_ptr<PixelBuffer> pixel_buffer)
{
    host render_host;
    render_host.start_host();
    render_host.connect_client();

    std::thread recv_thread_obj(recv_thread, std::ref(render_host), std::ref(command_queue));
    std::thread send_thread_obj(send_thread, std::ref(render_host), pixel_buffer);

    std::cout << "About to start render loop..." << std::endl;
    render_loop(command_queue, pixel_buffer);

    recv_thread_obj.join();
    send_thread_obj.join();
    
    std::cout << "Server: Stopping host" << std::endl;
    render_host.stop_host();
}

void wait_for_debugger() {
    std::cout << "Waiting for debugger to attach (PID: " << getpid() << ")...\n";

    // Simulate waiting for a debugger to attach
    std::this_thread::sleep_for(std::chrono::seconds(10));

    {
        std::lock_guard<std::mutex> lock(debugger_mtx);
        debugger_attached = true; // Signal that the debugger is attached
    }
    debugger_cv.notify_all(); // Notify waiting thread
}

int main()
{
    

    // Synchronization for debugger wait
    #ifdef DEBUG
    std::thread wait_thread([] {
        wait_for_debugger();
    });

    // Wait for the debugger to attach
    {
        std::unique_lock<std::mutex> lock(debugger_mtx);
        debugger_cv.wait(lock, [] { return debugger_attached.load(); });
    }
    wait_thread.join();
    std::cout << "Debugger attached! Continuing execution...\n";
    #endif


    CommandQueue command_queue;
    std::shared_ptr<PixelBuffer> pixelBuffer(std::make_shared<PixelBuffer>());

    server_init(command_queue, pixelBuffer);

    return 0;
}