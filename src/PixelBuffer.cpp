#include "PixelBuffer.h"


void PixelBuffer::write(const std::vector<float>& new_data) {
        std::lock_guard<std::mutex> lock(mtx);
        pixels = new_data;
        new_frame = true;
        std::cout << "Written to buffer!" << std::endl;
        cv.notify_one();
    }

bool PixelBuffer::read(std::vector<float>& out_data) {
        std::unique_lock<std::mutex> lock(mtx);
       if (!new_frame) {  // Check if a new frame is already available
        cv.wait(lock, [this]() { return new_frame; });
    }
        out_data = pixels;
        new_frame = false;
        return true;
    }

void PixelBuffer::resize(const int width, const int height)
{

    std::lock_guard<std::mutex> lock(mtx);
    std::cout << "Server: Width " << width << ", Height " << height << std::endl;

    this->width = width;
    this->height = height;
    new_frame = false;


    pixels.resize(width * height * 4); // Resize pixel buffer for new dimensions.
    std::fill(pixels.begin(), pixels.end(), 0);

}