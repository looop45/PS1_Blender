#pragma once
#include <vector>
#include <mutex>
#include <condition_variable>

class DrawData
{
    public:
        void write(const std::vector<uint8_t>& new_data);
    
        bool read(std::vector<uint8_t>& out_data);
    private:
        int width;
        int height;

        std::vector<uint8_t> pixels;
        std::mutex mtx;
        std::condition_variable cv;
        bool new_frame = false;
};

