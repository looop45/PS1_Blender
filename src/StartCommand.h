#pragma once
#include "Command.h"

class StartCommand : public Command
{
    public:
        StartCommand() : Command(ClientMessage::Start) {}

        void execute(Engine& engine) override
        {
            std::cout << "Starting engine!" << std::endl;
        }
};