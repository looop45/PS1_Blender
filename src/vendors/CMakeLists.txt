
#glad
#include_directories(${PROJECT_NAME} ${DEPEND_DIR}/glad/include)
add_library(glad STATIC glad/glad.c)
target_include_directories(glad 
    PUBLIC 
    ${CMAKE_CURRENT_SOURCE_DIR}/glad/include)