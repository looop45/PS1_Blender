#pragma once
#include <cstdint>

#define HEADER_SIZE 5

#pragma pack( push, 1 )
struct Header
{
    uint32_t message_size; // 4 bytes for size
    uint8_t message_type;  // 1 byte for type
};
#pragma pack( pop )

enum ClientMessage
{
    Start,
    Stop,
    Update,
    Draw,
};

enum ServerMessage
{
    Result,
};

