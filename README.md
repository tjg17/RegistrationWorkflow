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
Expected Algorithm Time: 270 seconds  
Loading Ultrasound Inputs... done (4.75 s)  
Preallocating Ultrasound Outputs... done (0.04 s)  
Loading MRI Inputs... done (4.58 s)  
Preallocating MRI Outputs... done (0.04 s)  
Centering volume... done (0.01 s)  
Transforming Ultrasound input... done (0.02 s)  
Smoothing label volume... done (1.65 s)  
Creating MR Model... done (1.97 s)  
Translating MRI inputs to U/S capsule... vtkMatrix4x4 (0x11b8aec0)  
  Debug: Off  
  Modified Time: 1497898  
  Reference Count: 1  
  Registered Events: (none)  
  Elements:  
    1 0 0 -8.38625   
    0 1 0 -13.1587   
    0 0 1 11.5093   
    0 0 0 1   
   
  
done (0.02 s)  
Creating MRI Model... Changing Label Value... done (0.05 s)  
done (0.65 s)  
Creating MRI Model... Changing Label Value... done (0.13 s)  
done (2.26 s)  
Converting Model to Label Map... done (4.31 s)  
Converting Model to Label Map... done (4.03 s)  
Smoothing label volume... done (2.08 s)  
Smoothing label volume... done (2.17 s)  
Smoothing label volume... done (2.32 s)  
Smoothing label volume... done (2.12 s)  
Resampling volumes to match ARFI... done (14.49 s)  
Additional Label Map Smoothing... done (14.06 s)  
Additional Label Map Smoothing... done (10.08 s)  
Additional Label Map Smoothing... done (5.44 s)  
Additional Label Map Smoothing... done (3.95 s)  
Converting Model to Label Map... done (57.17 s)  
Converting Model to Label Map... done (43.56 s)  
Converting Model to Label Map... done (43.46 s)  
Converting Model to Label Map... done (43.52 s)  
Creating Registration Label... Changing Label Value... done (0.11 s)  
Changing Label Value... done (0.11 s)  
Changing Label Value... done (0.11 s)  
Combining Labels... done (0.55 s)  
Thresholding Label Value... done (0.21 s)  
Thresholding Label Value... done (0.11 s)  
Combining Labels... done (0.46 s)  
done (1.65 s)  
Creating Registration Label... Changing Label Value... done (0.11 s)  
Changing Label Value... done (0.11 s)  
Changing Label Value... done (0.11 s)  
Combining Labels... done (0.53 s)  
Thresholding Label Value... done (0.21 s)  
Thresholding Label Value... done (0.11 s)  
Combining Labels... done (0.44 s)  
done (1.61 s)  
Changing Label Value... done (0.11 s)  
Changing Label Value... done (0.11 s)  
Changing Label Value... done (0.12 s)  
Changing Label Value... done (0.11 s)  
Changing Label Value... done (0.14 s)  
Changing Label Value... done (0.11 s)  
Changing Label Value... done (0.11 s)  
Changing Label Value... done (0.11 s)  
Changing Label Value... done (0.11 s)  
Changing Label Value... done (0.11 s)  
Changing Label Value... done (0.13 s)  
Processing completed  
Overall Algorithm Time:  273.3 seconds  
Overall Elapsed Time:  273.3 seconds  

Algorithm Output for no inputs supplied:  

Processing started  
Expected Algorithm Time: 270 seconds  
Loading Ultrasound Inputs... done (0.03 s)  
Preallocating Ultrasound Outputs... done (0.16 s)  
Loading MRI Inputs... done (0.01 s)  
Preallocating MRI Outputs... done (0.16 s)  
Input not present:  /invivo/Patient56/slicer/ARFI_Norm_HistEq.nii.gz  
Input not present:  /invivo/Patient56/slicer/Bmode.nii.gz  
Input not present:  /invivo/Patient56/slicer/ARFI_CC_Mask.nii.gz  
Input not present:  /invivo/Patient56/slicer/us_cap.vtk  
Input not present:  /invivo/Patient56/slicer/us_cg.vtk  
Input not present:  /invivo/Patient56/slicer/us_vm.vtk  
Input not present:  /invivo/Patient56/slicer/us_lesion1.vtk  
Input not present:  /invivo/Patient56/MRI_Images/T2/P56_no_PHI.nii.gz  
Input not present:  /invivo/Patient56/MRI_Images/P56_segmentation_final.nrrd  
Input not present:  /invivo/Patient56/MRI_Images/Anatomy/P56_zones_seg.nii.gz  
Input not present:  /invivo/Patient56/MRI_Images/Anatomy/P56_vm_seg.nrrd
Input not present:  /invivo/Patient56/MRI_Images/Cancer/P56_lesion1_seg.nrrd
Exiting process. Not all inputs supplied.
