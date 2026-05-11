import os

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import copy, load


class RasterioConan(ConanFile):
    name = "rasterio"
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    default_options = {
        "*/*:shared": True,
        # Trim heavy optional drivers — keep the demo build practical.
        "gdal/*:with_arrow": False,
    }

    def set_version(self):
        # Same file the conan-py-build backend reads via
        # [tool.conan-py-build.version].file — single source of truth.
        if self.version:
            return
        init_py = os.path.join(self.recipe_folder, "rasterio", "__init__.py")
        for line in load(self, init_py).splitlines():
            if line.startswith("__version__"):
                self.version = line.split("=", 1)[1].strip().strip("\"'")
                return

    def requirements(self):
        self.requires("gdal/3.12.1")
        self.requires("proj/9.7.0", override=True)
        # Avoid CMake 4 incompatibility in older transitive recipes.
        self.requires("geos/3.13.0", override=True)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure(
            variables={
                "GDAL_VERSION_STR": str(self.dependencies["gdal"].ref.version),
            }
        )
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        gdal_res = os.path.join(self.dependencies["gdal"].package_folder, "res", "gdal")
        copy(
            self,
            "*",
            src=gdal_res,
            dst=os.path.join(self.package_folder, "rasterio", "gdal_data"),
        )

        proj_res = os.path.join(self.dependencies["proj"].package_folder, "res")
        copy(
            self,
            "*",
            src=proj_res,
            dst=os.path.join(self.package_folder, "rasterio", "proj_data"),
        )
