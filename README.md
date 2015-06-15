# RegistrationWorkflow
This repository contains a Python scripted extension for 3D Slicer to process ARFI/Bmode ultrasound volumes and T2 MRI volumes as well as capsule segmentations prior to an image-based segmentation using the "Distance Map Based Registration" available in the SlicerProstate module.  

To use this extension for the  first time:  

1) Clone repository into local directory (e.g. ~/home/user/RegistrationWorkflow)  
2) Open 3D Slicer version 4.4 or above  
3) Select "Extension Wizard" module in search box  
4) Under "Extension Tools", choose "Select Extension" and choose ~/home/user/RegistrationWorkflow  
5) When prompted, be sure load all modules and check the "Add selected module to search paths" box.  
6) Modules can be selected by searching in the search box in the toolbar  


Example Output to Slicer CLI of this extension:  

Processing started  
Expected Run Time: 100 seconds  
Centering volume... done (0.01 s)  
Centering volume... done (0.01 s)  
Transforming Ultrasound inputs... done (0.02 s)  
Ultrasound:  Converting Model to Label Map... done (40.23 s)  
Creating MR Model... done (0.82 s)  
Translating T2 volume and MRI model... done (0.02 s)  
Resampling T2 volume to match ARFI... done (3.59 s)  
MRI:  Converting Model to Label Map... done (39.30 s)  
Processing completed  
Overall Run Time:  84.0 seconds  
