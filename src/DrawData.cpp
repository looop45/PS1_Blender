#include "DrawData.h"

void DrawData::write(const std::vector<uint8_t>& new_data) {
        std::lock_guard<std::mutex> lock(mtx);
        pixels = new_data;
        new_frame = true;
        cv.notify_one();
    }

bool DrawData::read(std::vector<uint8_t>& out_data) {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, [this]() { return new_frame; });
        out_data = pixels;
        new_frame = false;
        return true;
    }