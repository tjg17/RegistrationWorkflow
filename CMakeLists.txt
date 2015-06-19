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
add_subdirectory(T2Process)
add_subdirectory(ListModuleParams)
add_subdirectory(Distance Map Based Registration)
add_subdirectory(DistanceMapBasedRegistration)
add_subdirectory(Prostate Distance Map Registration)
add_subdirectory(New Module)
add_subdirectory(New Module)
add_subdirectory(Distance Map Registration)
add_subdirectory(DistanceMapRegister)
add_subdirectory(PreProcess)
add_subdirectory(Segmentation Smoothing)
add_subdirectory(Quad Edge Surface Mesher)
add_subdirectory(Distance Map Based Registration)
add_subdirectory(SegmentationSmoothing)
add_subdirectory(Custom Distance Map Register)
add_subdirectory(CustomDistanceMapRegistration)
add_subdirectory(CustomRegister)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
