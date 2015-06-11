cmake_minimum_required(VERSION 2.8.9)

project(RegistrationWorkflow)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/tjg17/RegistrationWorkflow")
set(EXTENSION_CATEGORY "Registration")
set(EXTENSION_CONTRIBUTORS "Tyler Glass (Nightingale Lab)")
set(EXTENSION_DESCRIPTION "Code to do MRI and US processing prior to registration.")
set(EXTENSION_ICONURL "https://raw.github.com/tjg17/RegistrationWorkflow/master/RegistrationWorkflow.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/RegistrationWorkflow/Screenshots/1.png")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(UltrasoundProcess)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
