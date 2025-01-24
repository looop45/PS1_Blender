#pragma once
#include <vector>
#include <mutex>
#include <condition_variable>
#include <iostream>
#include <cstdint>



class PixelBuffer
{
    public:
        void write(const std::vector<float>& new_data);

        void resize(const int width, const int height);
    
        bool read(std::vector<float>& out_data);
        bool new_frame = false;
    private:
        uint16_t width;
        uint16_t height;

        std::vector<float> pixels;
        std::mutex mtx;
        std::condition_variable cv;
};

