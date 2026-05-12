# Build tools provided by the manylinux container via yum (perl-core m4
# autoconf automake libtool pkgconfig). Conan would otherwise rebuild them
# from sources, which is fragile inside the minimal AlmaLinux 8 image —
# m4's configure runs a sigsegv-detection test that fails in restricted
# containers, producing a binary that autom4te then rejects.
#
# These tools only run at build time; nothing from them ends up in the
# wheel. The user-facing host stack (gdal, proj, geos, libcurl, openssl,
# ...) is still built by Conan with its own settings/options.
[platform_tool_requires]
m4/1.4.19
autoconf/2.71
automake/1.16.5
libtool/2.4.7
pkgconf/2.2.0
