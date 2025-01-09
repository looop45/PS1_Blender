cmake_minimum_required(VERSION 3.10)
project(PS1_Render_Engine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(VENDOR_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src/vendors")
set(SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src")

# Configure RPATH so libraries are found after make install
if(APPLE)
    set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib")
elseif(UNIX)
    set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib64")
endif()

add_executable(${PROJECT_NAME})

add_subdirectory(${SRC_DIR})
add_subdirectory(${VENDOR_DIR})

find_package(glfw3 3.3 REQUIRED)
find_package(OpenGL REQUIRED)

target_link_libraries(${PROJECT_NAME}
        PRIVATE
        glfw
        glad
        ${PXR_LIBRARIES}
)