cmake_minimum_required(VERSION 3.18)
project(rasterio LANGUAGES C CXX)

find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module NumPy)
find_package(GDAL REQUIRED CONFIG)

find_program(CYTHON_EXE cython REQUIRED)

# Parse GDAL version (passed from conanfile via -DGDAL_VERSION_STR=x.y.z)
string(REGEX MATCHALL "[0-9]+" _gdal_version_parts "${GDAL_VERSION_STR}")
list(LENGTH _gdal_version_parts _n_parts)
if(_n_parts LESS 3)
    message(FATAL_ERROR "GDAL_VERSION_STR must be x.y.z, got '${GDAL_VERSION_STR}'")
endif()
list(GET _gdal_version_parts 0 GDAL_MAJOR)
list(GET _gdal_version_parts 1 GDAL_MINOR)
list(GET _gdal_version_parts 2 GDAL_PATCH)
message(STATUS "Building against GDAL ${GDAL_MAJOR}.${GDAL_MINOR}.${GDAL_PATCH}")

set(RASTERIO_SRC ${CMAKE_CURRENT_SOURCE_DIR}/rasterio)

# All .pxd/.pxi files — added as DEPENDS so any edit re-cythonizes.
file(GLOB CYTHON_DEPS
    ${RASTERIO_SRC}/*.pxd
    ${RASTERIO_SRC}/*.pxi
)

function(add_cython_module name)
    cmake_parse_arguments(CY "CXX" "" "" ${ARGN})

    set(_ext c)
    set(_cplus "")
    if(CY_CXX)
        set(_ext cpp)
        set(_cplus --cplus)
    endif()

    set(_generated ${CMAKE_CURRENT_BINARY_DIR}/${name}.${_ext})
    set(_pyx ${RASTERIO_SRC}/${name}.pyx)

    add_custom_command(
        OUTPUT ${_generated}
        COMMAND ${CYTHON_EXE}
            ${_cplus}
            -3
            --module-name rasterio.${name}
            -I ${CMAKE_CURRENT_SOURCE_DIR}
            -E CTE_GDAL_MAJOR_VERSION=${GDAL_MAJOR}
            -E CTE_GDAL_MINOR_VERSION=${GDAL_MINOR}
            -E CTE_GDAL_PATCH_VERSION=${GDAL_PATCH}
            -X freethreading_compatible=True
            --output-file ${_generated}
            ${_pyx}
        DEPENDS ${_pyx} ${CYTHON_DEPS}
        COMMENT "Cythonizing rasterio.${name}"
        VERBATIM
    )

    Python3_add_library(${name} MODULE WITH_SOABI ${_generated})

    target_include_directories(${name} PRIVATE ${RASTERIO_SRC})
    target_link_libraries(${name} PRIVATE Python3::NumPy GDAL::GDAL)

    if(NOT MSVC)
        target_compile_options(${name} PRIVATE
            -Wno-unused-parameter
            -Wno-unused-function
        )
    endif()

    if(CY_CXX)
        target_compile_features(${name} PRIVATE cxx_std_11)
        if(APPLE)
            target_compile_options(${name} PRIVATE
                -mmacosx-version-min=10.9
                -stdlib=libc++
            )
        endif()
    endif()

    install(TARGETS ${name} DESTINATION rasterio)
endfunction()

# C extensions
add_cython_module(_base)
add_cython_module(_io)
add_cython_module(_features)
add_cython_module(_env)
add_cython_module(_err)
add_cython_module(_example)
add_cython_module(_version)
add_cython_module(_transform)
add_cython_module(_vsiopener)
add_cython_module(cache)
add_cython_module(crs)
add_cython_module(shutil)

# C++ extensions
add_cython_module(_warp CXX)
add_cython_module(_fill CXX)
add_cython_module(_filepath CXX)
