# m4 from the system: Conan's m4 fails its own sigsegv-detection runtime
# test in the minimal AlmaLinux 8 manylinux container, producing a binary
# that autom4te rejects. System m4 (yum install m4) is plain GNU 1.4.18
# and works fine.
#
# autoconf / automake / libtool intentionally NOT listed: AlmaLinux 8's
# versions (1.16.1, 2.69, 2.4.6) are too old for modern recipes like
# libcurl/8.20.0 that pin automake>=1.18. We let Conan build those — they
# in turn pick up system m4 via this platform_tool_requires entry.
[platform_tool_requires]
m4/1.4.19
