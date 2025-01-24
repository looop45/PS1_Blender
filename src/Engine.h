#pragma once
#include "PixelBuffer.h"
#include "Camera.h"

#include <glad.h>
#include <GLFW/glfw3.h>
#include <iostream>

class Engine
{
    public:
        Engine(std::shared_ptr<PixelBuffer>& buffer);
        ~Engine();

        void draw(Camera camera, int width, int height);


    private:
        void InitGLFW(const char* title);
        bool InitGlad();
        void ShutdownGLFW();
        GLuint texture;
        GLuint framebuffer;

        GLFWwindow* window;
        std::shared_ptr<PixelBuffer> buffer;

};


