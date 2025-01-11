#pragma once
#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <atomic>

#include "json.hpp"

using json = nlohmann::json;

// Thread-safe queue for commands
class CommandQueue {
public:
    void push(const json& cmd) {
        std::lock_guard<std::mutex> lock(mtx);
        commands.push(cmd);
        cv.notify_one();
    }

    bool pop(json& cmd) {
        std::unique_lock<std::mutex> lock(mtx);
        if (commands.empty()) return false;
        cmd = commands.front();
        commands.pop();
        return true;
    }

    void wait_and_pop(json& cmd) {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, [this]() { return !commands.empty(); });
        cmd = commands.front();
        commands.pop();
    }

private:
    std::queue<json> commands;
    std::mutex mtx;
    std::condition_variable cv;
};