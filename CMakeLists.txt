cmake_minimum_required(VERSION 3.12)
project(MIPSolver LANGUAGES CXX C)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 设置保护性编译选项
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    if(WIN32)
        set(CMAKE_CXX_FLAGS_RELEASE "/O2 /DNDEBUG /MT")
    elseif(APPLE)
        # macOS特殊设置，避免链接器警告
        set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG -fvisibility=hidden")
    else()
        set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG -fvisibility=hidden")
    endif()
endif()

# 创建核心算法库（不包含main.cpp）
file(GLOB CORE_SOURCES "src/*.cpp")
list(REMOVE_ITEM CORE_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp")

# 核心算法编译成静态库
add_library(mipsolver_core STATIC ${CORE_SOURCES})
target_include_directories(mipsolver_core PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/src")

# 设置库的可见性（隐藏内部符号）
if(NOT WIN32)
    set_target_properties(mipsolver_core PROPERTIES
        CXX_VISIBILITY_PRESET hidden
        VISIBILITY_INLINES_HIDDEN ON
    )
endif()

# 创建C API共享库（可选）
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/api/mipsolver_c_api.cpp")
    add_library(mipsolver_shared SHARED api/mipsolver_c_api.cpp)
    target_link_libraries(mipsolver_shared PRIVATE mipsolver_core)
    target_include_directories(mipsolver_shared PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/api")
    
    # Windows DLL导出设置
    if(WIN32)
        target_compile_definitions(mipsolver_shared PRIVATE MIPSOLVER_EXPORTS)
        set_target_properties(mipsolver_shared PROPERTIES
            WINDOWS_EXPORT_ALL_SYMBOLS ON
        )
    endif()
    
    # 设置输出名称
    set_target_properties(mipsolver_shared PROPERTIES 
        OUTPUT_NAME "mipsolver"
        VERSION 1.0.0
        SOVERSION 1
    )
endif()

# 可执行文件（可选）
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp")
    add_executable(main src/main.cpp)
    target_link_libraries(main PRIVATE mipsolver_core)
    target_include_directories(main PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/src")
endif()

# Python绑定
option(BUILD_PYTHON_BINDINGS "Build Python bindings" ON)

if(BUILD_PYTHON_BINDINGS)
    find_package(pybind11 REQUIRED)
    
    # Python模块 - 这将被打包到wheel中
    pybind11_add_module(mipsolver._solver bindings/python_bindings.cpp)
    
    # 链接到核心库
    target_link_libraries(mipsolver._solver PRIVATE mipsolver_core)
    
    # 确保Python模块找不到源码
    target_compile_definitions(mipsolver._solver PRIVATE VERSION_INFO="${PROJECT_VERSION}")
    
    # Windows特殊设置
    if(WIN32 AND TARGET mipsolver_shared)
        target_link_libraries(mipsolver PRIVATE mipsolver_shared)
    endif()
endif()

# 安装规则
if(TARGET mipsolver_shared)
    install(TARGETS mipsolver_core mipsolver_shared
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin
    )
else()
    install(TARGETS mipsolver_core
        ARCHIVE DESTINATION lib
    )
endif()

if(TARGET main)
    install(TARGETS main RUNTIME DESTINATION bin)
endif()