#include <iostream>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <glad.h>
#include <GLFW/glfw3.h>

#include "CommandQueue.h"
#include "Scene.h"
#include "host.h"

// Global variables
std::atomic<bool> running(true);
Scene shared_scene;
std::mutex scene_mtx;


GLFWwindow* InitGLFW(const char* title)
{
    //Set GLFW window options
    glfwInit();
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);

    //Initialize Window
    GLFWwindow* window = glfwCreateWindow(800, 600, title, NULL, NULL);
    if (window == NULL)
    {
        std::cout << "Failed to create GLFW window" << std::endl;
        glfwTerminate();
        return NULL;
    }
    glfwMakeContextCurrent(window);

    //glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);  

    return window;
}

bool InitGlad()
{
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress))
    {
        std::cout << "Failed to initialize GLAD" << std::endl;
        return false;
    } 
    return true;
}

void ShutdownGLFW(GLFWwindow* window)
{
    glfwDestroyWindow(window);
    glfwTerminate();
}

void server_thread(CommandQueue& command_queue)
{
    host render_host;
    render_host.start_host();
    render_host.connect_client();

    while (running) 
    {
        if (render_host.handle_client(command_queue) == 0)
        {
            running = false;
            break;
        }
    }

    render_host.stop_host();
}

int render_loop(CommandQueue& command_queue) {
    // Initialize OpenGL context here.
    GLFWwindow* window = InitGLFW("PS1 Render");
    std::cout << "running render thread!" << std::endl;

    if (!window || !InitGlad()) 
    {
        std::cout << "Failed to launch window!" << std::endl;
        return 1;
    }
    while (running) 
    {
        //Render Loop

            //check and call events and swap the buffers
            glfwPollEvents();

            //ImGui::ShowDemoWindow(); // Show demo window! :)

            // Rendering
            glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
            glClear(GL_COLOR_BUFFER_BIT);

            glfwSwapBuffers(window);

        /*
        Command cmd;
        if (command_queue.pop(cmd)) {
            // Process draw command
            std::cout << "Processing command: " << cmd.action << std::endl;

            // Perform rendering based on the command
        }

        // Optionally update rendering based on the scene
        {
            std::lock_guard<std::mutex> lock(scene_mtx);
            // Use shared_scene for rendering
        }

        // Perform rendering (e.g., OpenGL draw calls).*/
    }

    //Shutdown
    ShutdownGLFW(window);
    return 0;
}

int main()
{
    CommandQueue command_queue;

    std::thread server(server_thread, std::ref(command_queue));

    render_loop(command_queue);

    server.join();

    return 0;
}