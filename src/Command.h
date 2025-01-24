#pragma once
#include <iostream>
#include <memory>
#include <vector>
#include <functional>

#include "Messages.h"
#include "Engine.h"

class Command
{
    public:
        explicit Command(ClientMessage type) : type(type) {}
        virtual ~Command() = default;
        ClientMessage getType() const {return type;}

        virtual void execute(Engine& engine) = 0;

    private:
        ClientMessage type;
};