# - Try to find NIX
# Once done this will define
#  NIX_FOUND - System has Nix
#  NIX_INCLUDE_DIRS - The Nix include directories
#  NIX_LIBRARIES - The libraries needed to use Nix


find_path(NIX_INCLUDE_DIR nix.hpp
  HINTS /usr/local/include
  /usr/include
  $ENV{NIX_ROOT}/include
  PATH_SUFFIXES nix)

find_library(NIX_LIBRARY NAMES nix libnix
  HINTS ${NIX_INCLUDE_DIR}/../lib
  HINTS ${NIX_INCLUDE_DIR}/../build
  /usr/local/lib
  /usr/lib)

set(NIX_LIBRARIES ${NIX_LIBRARY} )
set(NIX_INCLUDE_DIRS ${NIX_INCLUDE_DIR} )

include(FindPackageHandleStandardArgs)
# handle the QUIETLY and REQUIRED arguments and set NIX_FOUND to TRUE
# if all listed variables are TRUE
find_package_handle_standard_args(Nix DEFAULT_MSG
  NIX_LIBRARY NIX_INCLUDE_DIR)

mark_as_advanced(NIX_INCLUDE_DIR NIX_LIBRARY)

