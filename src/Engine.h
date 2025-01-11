#include "DrawData.h"
#include "Camera.h"
#include "json.hpp"

#include <glad.h>
#include <GLFW/glfw3.h>
#include <iostream>

using json = nlohmann::json;

class Engine
{
    public:
        Engine();
        ~Engine();

        std::vector<uint8_t> handleCommand(const json& cmd);

    private:
        std::vector<uint8_t> draw(Camera camera, int width, int height);

        void InitGLFW(const char* title);
        bool InitGlad();
        void ShutdownGLFW();

        GLFWwindow* window;
        

};


