# RegistrationWorkflow
This repository contains a Python scripted extension for 3D Slicer to process ARFI/Bmode ultrasound volumes and T2 MRI volumes and segmentations prior to an image-based registration using the "Distance Map Based Registration" available in the SlicerProstate module.  

To use this extension for the  first time:  

1) Clone repository into local directory (e.g. ~/home/user/RegistrationWorkflow)  
2) Open 3D Slicer version 4.4 or above  
3) Select "Extension Wizard" module in search box  
4) Under "Extension Tools", choose "Select Extension" and choose ~/home/user/RegistrationWorkflow  
5) When prompted, be sure load all modules and check the "Add selected module to search paths" box.  
6) Modules can be selected by searching in the search box in the toolbar  


Example Output to Slicer Command Line Interface of this extension:  

Processing started  
Expected Algorithm Time: 95 seconds  
Centering volume... done (0.17 s)  
Transforming Ultrasound input... done (0.06 s)  
Smoothing label volume... done (2.25 s)  
Creating MR Model... done (1.94 s)  
Translating MRI inputs to U/S capsule... done (0.09 s)  
Creating MR Model... done (0.49 s)  
Converting Model to Label Map... done (3.57 s)  
Converting Model to Label Map... done (3.36 s)  
Smoothing label volume... done (2.09 s)  
Smoothing label volume... done (2.11 s)  
Smoothing label volume... done (2.33 s)  
Smoothing label volume... done (2.16 s)  
Resampling volumes to match ARFI... done (13.59 s)  
Converting Model to Label Map... done (37.55 s)  
Additional Label Map Smoothing... done (7.71 s)  
Additional Label Map Smoothing... done (4.55 s)  
Additional Label Map Smoothing... done (5.56 s)  
Additional Label Map Smoothing... done (3.83 s)  
Changing Label Value... done (0.13 s)  
Changing Label Value... done (0.13 s)  
Changing Label Value... done (0.13 s)  
Changing Label Value... done (0.13 s)  
Changing Label Value... done (0.11 s)  
Removing unnecessary nodes from MRML scene... done (0.08 s)  
Removing unnecessary nodes from MRML scene... done (0.09 s)  
Saving Ultrasound Results... done (5.14 s)  
Saving MRI Results... done (4.76 s)  
Saving MRML Scene... done (2.10 s)  
Processing completed  
Overall Algorithm Time:  94.2 seconds  
Overall Saving Time:  12.0 seconds  
Overall Elapsed Time:  106.2 seconds  
