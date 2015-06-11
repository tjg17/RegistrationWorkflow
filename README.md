# RegistrationWorkflow
This repository contains python code used in 3D Slicer to process ARFI/Bmode ultrasound volumes and T2 MRI volumes as well as various segmentations prior to an image-based segmentation using the "Distance Map Based Registration" available in the SlicerProstate module.

To use this extension for the  first time:

\n1) Clone repository into local directory (e.g. ~/home/user/RegistrationWorkflow)
2) Open 3D Slicer version 4.4 or above 
3) Select "Extension Wizard" module in search box
4) Under "Extension Tools", choose "Select Extension" and choose ~/home/user/RegistrationWorkflow
5) When prompted, be sure load all modules and check the "Add selected module to search paths" box.
6) Modules can be selected by searching in the search box in the toolbar


To edit code for a module of this extension:

1) Edit the ~/home/user/RegistrationWorkflow/modulename/modulename.py file for the given module
2) Select the module in 3D Slicer and use the "Reload" option after editing code
3) Troubleshooting code can be done using Python Interactor (Ctrl+3 or View->Python Interactor)
