from conans import ConanFile, CMake, tools
import os


class FlecsConan(ConanFile):
    name = "flecs"
    description = "A fast entity component system (ECS) for C & C++"
    license = "MIT"
    topics = ("gamedev", "cpp", "data-oriented-design", "c99",
              "game-development", "ecs", "entity-component-system",
              "cpp11", "ecs-framework")
    homepage = "https://github.com/SanderMertens/flecs"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()        
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build(target="flecs" if self.options.shared else "flecs_static")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["flecs"] if self.options.shared else ["flecs_static"]
        if not self.options.shared:
            self.cpp_info.defines.append("flecs_STATIC")
