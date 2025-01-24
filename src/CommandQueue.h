#pragma once
#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <atomic>

#include "Command.h"

// Thread-safe queue for commands
class CommandQueue {
public:
    void push(std::shared_ptr<Command> cmd) {
        std::lock_guard<std::mutex> lock(mtx);
        commands.push(cmd);
        cv.notify_one();
    }

    bool pop(std::shared_ptr<Command>& cmd) {
        std::unique_lock<std::mutex> lock(mtx);
        if (commands.empty()) return false;
        cmd = commands.front();
        commands.pop();
        return true;
    }

    void wait_and_pop(std::shared_ptr<Command> cmd) {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, [this]() { return !commands.empty(); });
        cmd = commands.front();
        commands.pop();
    }

private:
    std::queue<std::shared_ptr<Command>> commands;
    std::mutex mtx;
    std::condition_variable cv;
};