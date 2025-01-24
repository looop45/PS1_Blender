#pragma once
#include "Command.h"

class DrawCommand : public Command
{
    public:
        DrawCommand(int width, int height) : Command(ClientMessage::Draw) 
        {
            this->width = width;
            this->height = height;
        }

        void execute(Engine& engine) override
        {
            Camera camera;
            engine.draw(camera, width, height);
        }

    private:
        int width;
        int height;
};