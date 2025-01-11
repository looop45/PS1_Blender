# Include directories for headers
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

#include include directory
target_include_directories(${PROJECT_NAME}
    PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/vendors/include
)

# Add other source files
target_sources(${PROJECT_NAME}
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp
        ${CMAKE_CURRENT_SOURCE_DIR}/host.h
        ${CMAKE_CURRENT_SOURCE_DIR}/CommandQueue.h
        ${CMAKE_CURRENT_SOURCE_DIR}/Engine.h
        ${CMAKE_CURRENT_SOURCE_DIR}/Engine.cpp
        ${CMAKE_CURRENT_SOURCE_DIR}/DrawData.h
        ${CMAKE_CURRENT_SOURCE_DIR}/DrawData.cpp
        ${CMAKE_CURRENT_SOURCE_DIR}/vendors/include/json.hpp
)