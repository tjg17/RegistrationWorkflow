import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import time # for measuring time of processing steps


def numericInputFrame(parent, label, tooltip, minimum, maximum, step, decimals):
    inputFrame = qt.QFrame(parent)
    inputFrame.setLayout(qt.QHBoxLayout())
    inputLabel = qt.QLabel(label, inputFrame)
    inputLabel.setToolTip(tooltip)
    inputFrame.layout().addWidget(inputLabel)
    inputSpinBox = qt.QDoubleSpinBox(inputFrame)
    inputSpinBox.setToolTip(tooltip)
    inputSpinBox.minimum = minimum
    inputSpinBox.maximum = maximum
    inputSpinBox.singleStep = step
    inputSpinBox.decimals = decimals
    inputFrame.layout().addWidget(inputSpinBox)
    return inputFrame, inputSpinBox

#
# PreProcess
#

class PreProcess(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "PreProcess" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Custom"]
    self.parent.dependencies = []
    self.parent.contributors = ["Tyler Glass (Nightingale Lab)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is a scripted loadable module bundled in an extension.
    It performs pre-processing for T2-MRI and ARFI/Bmode volumes and segemntations prior to registration.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# PreProcessWidget
#

class PreProcessWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...


    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Patient Information"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    PatientNumberMethodFrame = qt.QFrame(self.parent)
    parametersFormLayout.addWidget(PatientNumberMethodFrame)
    PatientNumberMethodFormLayout = qt.QFormLayout(PatientNumberMethodFrame)
    PatientNumberIterationsFrame, self.PatientNumberIterationsSpinBox = numericInputFrame(self.parent,"Patient Number:","Tooltip",56,110,1,0)
    PatientNumberMethodFormLayout.addWidget(PatientNumberIterationsFrame)

    self.SaveDataCheckBox = qt.QCheckBox("Save Results to Disk")
    self.SaveDataCheckBox.checked = False
    parametersFormLayout.addWidget(self.SaveDataCheckBox)

    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = True
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    
    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = True

  def onApplyButton(self):
    logic = PreProcessLogic()
    logic.run(str(int(self.PatientNumberIterationsSpinBox.value)), self.SaveDataCheckBox.checked)
# PreProcessLogic
#

class PreProcessLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() == None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidUltrasoundData(self, VolumeNode1, VolumeNode2, VolumeNode3, ModelNode1, ModelNode2):
    """Validates if ultrasound data is defined
    """
    if not inputVolumeNode1:
      logging.debug('isValidInputOutputData failed: no input ARFI volume node defined')
      return False
    if not inputVolumeNode2:
      logging.debug('isValidInputOutputData failed: no input Bmode volume node defined')
      return False
    if not inputModelNode:
      logging.debug('isValidInputOutputData failed: no input capsule model node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output capsule labelmap node defined')
      return False
    if inputVolumeNode1.GetID()==inputVolumeNode2.GetID():
      logging.debug('isValidInputOutputData failed: ARFI and Bmode inputs are the same node.')
      return False
    return True

  def isValidMRIData(self, inputVolumeNode1, inputVolumeNode2, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode1:
      logging.debug('isValidInputOutputData failed: no input T2-MRI volume node defined')
      return False
    if not inputVolumeNode2:
      logging.debug('isValidInputOutputData failed: no input T2 capsule segmentation volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output capsule labelmap node defined')
      return False
    if inputVolumeNode1.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: Input and output segmentation are the same node. Create a new output volume to avoid this error.')
      return False
    return True

  def CenterVolume(self, *inputVolumes):
    """ Centers an inputted volume using the image spacing, size, and origin of the volume
    """
    # Print to Slicer CLI
    print('Centering volume...'),
    start_time = time.time()

    for inputVolume in inputVolumes: # cycle through all input volumes

        # Use image size and spacing to find origin coordinates
        extent = [x-1 for x in inputVolume.GetImageData().GetDimensions()] # subtract 1 from dimensions to get extent
        spacing = [x for x in inputVolume.GetSpacing()]
        new_origin = [a*b/2 for a,b in zip(extent,spacing)]
        new_origin[2] = -new_origin[2] # need to make this value negative to center the volume

        # Set input volume origin to the new origin
        inputVolume.SetOrigin(new_origin)

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def US_transform(self, *ARFIinputs):
    """ Performs inversion transform with [1 1 -1 1] diagonal entries on Ultrasound inputs
    """
    # Print to Slicer CLI
    print('Transforming Ultrasound input...'),
    start_time = time.time()

    # Create inverting transform matrix
    invert_transform = vtk.vtkMatrix4x4()
    invert_transform.SetElement(2,2,-1) # put a -1 in 3rd entry of diagonal of matrix

    # Apply transform to all input nodes
    for ARFIinput in ARFIinputs:
        ARFIinput.ApplyTransformMatrix(invert_transform)
    # inputARFI.ApplyTransformMatrix(invert_transform)
    # inputBmode.ApplyTransformMatrix(invert_transform)
    # inputCC.ApplyTransformMatrix(invert_transform)
    # inputUSCaps_Model.ApplyTransformMatrix(invert_transform)
    # inputUSCG_Model.ApplyTransformMatrix(invert_transform)

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def ModelToLabelMap(self, inputVolume, inputModel, outputVolume, sampleDistance):
    """ Converts models into a labelmap on the input T2-MRI volume using sample distance  provided(smaller than smallest pixel width in input volume)
    """
    # Print to Slicer CLI
    print('Converting Model to Label Map...'),
    start_time = time.time()

    # Get spacing of inputVolume and multiply by 0.8 to determine sample distance
    # samplevoxeldistance = round(0.8*min(inputVolume.GetSpacing()),2) # rounds to 2 decimal points for 80% of smallest voxel

    # Run the slicer module in CLI
    cliParams = {'InputVolume': inputVolume.GetID(), 'surface': inputModel.GetID(), 'OutputVolume': outputVolume.GetID(), 'sampleDistance': sampleDistance, 'labelValue': 10}
    cliNode = slicer.cli.run(slicer.modules.modeltolabelmap, None, cliParams, wait_for_completion=True)
    
    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def MRCapModelMaker(self, inputMRlabel):
    """ Converts MRI labelmap segemntation into slicer VTK model node
    """
    # Print to Slicer CLI
    print('Creating MR Model...'),
    start_time = time.time()

    # Set model parameters
    parameters = {} 
    parameters["InputVolume"] = inputMRlabel.GetID()
    parameters['FilterType'] = "Laplacian"
    parameters['GenerateAll'] = True
    parameters["JointSmoothing"] = True
    parameters["SplitNormals"] = False
    parameters["PointNormals"] = False
    parameters["SkipUnNamed"] = False
    parameters["StartLabel"] = -1
    parameters["EndLabel"] = -1
    parameters["Decimate"] = 0.1
    parameters["Smooth"] = 70
    parameters["Name"] = 'mr-cap'

    # Need to create new model heirarchy node for models to enter the scene
    numNodes = slicer.mrmlScene.GetNumberOfNodesByClass( "vtkMRMLModelHierarchyNode" )
    if numNodes > 0:
      # user wants to delete any existing models, so take down hierarchy and
      # delete the model nodes
      rr = range(numNodes)
      rr.reverse()
      for n in rr:
        node = slicer.mrmlScene.GetNthNodeByClass( n, "vtkMRMLModelHierarchyNode" )
        slicer.mrmlScene.RemoveNode( node.GetModelNode() )
        slicer.mrmlScene.RemoveNode( node )

    # Create new output model heirarchy
    outHierarchy = slicer.vtkMRMLModelHierarchyNode()
    outHierarchy.SetScene( slicer.mrmlScene )
    outHierarchy.SetName( "MRI Models" )
    slicer.mrmlScene.AddNode( outHierarchy )

    # Set the parameter for the output model heirarchy
    parameters["ModelSceneFile"] = outHierarchy

    # Run the module from the command line
    slicer.cli.run(slicer.modules.modelmaker, None, parameters, wait_for_completion=True)

    # Define the output model as the created model in the scene
    outputMRModel = slicer.util.getNode('mr-cap_1_1') # cap label has label value of 1 so model created is Model_1_1

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

    return outputMRModel    

  def MRModelMaker(self, inputMRlabel, smoothingValue):
    """ Converts MRI tumor labelmap segemntation into slicer VTK model node
    """
    # Print to Slicer CLI
    print('Creating MRI Model...'),
    start_time = time.time()

    # Change input label value
    self.ThresholdScalarVolume(inputMRlabel,  34)

    # Set model parameters
    parameters = {} 
    parameters["InputVolume"] = inputMRlabel.GetID()
    parameters['FilterType'] = "Laplacian"
    parameters['GenerateAll'] = True
    parameters["JointSmoothing"] = True
    parameters["SplitNormals"] = False
    parameters["PointNormals"] = False
    parameters["SkipUnNamed"] = False
    parameters["StartLabel"] = -1
    parameters["EndLabel"] = -1
    parameters["Decimate"] = 0.1
    parameters["Smooth"] = int(smoothingValue) # make sure it is an integer
    parameters["Pad"] = True
    parameters["Name"] = 'model'

    # # Need to create new model heirarchy node for models to enter the scene
    # numNodes = slicer.mrmlScene.GetNumberOfNodesByClass( "vtkMRMLModelHierarchyNode" )
    # if numNodes > 0:
    #   # user wants to delete any existing models, so take down hierarchy and
    #   # delete the model nodes
    #   rr = range(numNodes)
    #   rr.reverse()
    #   for n in rr:
    #     node = slicer.mrmlScene.GetNthNodeByClass( n, "vtkMRMLModelHierarchyNode" )
    #     slicer.mrmlScene.RemoveNode( node.GetModelNode() )
    #     slicer.mrmlScene.RemoveNode( node )

    # Create new output model heirarchy
    outHierarchy = slicer.vtkMRMLModelHierarchyNode()
    outHierarchy.SetScene( slicer.mrmlScene )
    outHierarchy.SetName( ('MRI Models Smooth '+ str(smoothingValue)) )
    slicer.mrmlScene.AddNode( outHierarchy )

    # Set the parameter for the output model heirarchy
    parameters["ModelSceneFile"] = outHierarchy

    # Run the module from the command line
    slicer.cli.run(slicer.modules.modelmaker, None, parameters, wait_for_completion=True)

    # Define the output model as the created model in the scene
    outputMRModel = slicer.util.getNode('model_34_34') # created model has label value of 34 

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

    return outputMRModel  


  def MR_translate(self, movingMRIModel, fixedUSModel, *MRIinputs): 
    """ Translates MRI capsule and T2 imaging volume to roughly align with US capsule model so T2 prostate is within ARFI image
    """
    # Print to Slicer CLI
    print('Translating MRI inputs to U/S capsule...'),
    start_time = time.time()

    # Find out coordinates of models to be used for translation matrix
    moving_bounds = movingMRIModel.GetPolyData().GetBounds()
    fixed_bounds  =   fixedUSModel.GetPolyData().GetBounds()

    
    # Define transform matrix
    translate_transform = vtk.vtkMatrix4x4()
    translate_transform.SetElement(2,3,fixed_bounds[5] - moving_bounds[5]) # lines up base of prostate 
    translate_transform.SetElement(1,3,fixed_bounds[2] - moving_bounds[2]) # lines up posterior of prostate 
    translate_transform.SetElement(0,3,fixed_bounds[0] - moving_bounds[0]) # lines up right side of prostate 
    
    # OPTIONAL: print transform to Python CLI
    print translate_transform 

    # Apply transform to all MRI inputs
    for MRIinput in MRIinputs:
        MRIinput.ApplyTransformMatrix(translate_transform)

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)
  
  def SegmentationSmoothing(self, inputVolume, outputsmoothedVolume, *labelNumber):
    """ Smooths an input volume into an outputVolume using the Segmentation Smoothing Module from SlicerProstate module
    """
    # Print to Slicer CLI
    print('Smoothing label volume...'),
    start_time = time.time()

    # Define parameters for smoothing
    parameters = {}
    parameters["inputImageName"]= inputVolume.GetID()
    parameters["outputImageName"]= outputsmoothedVolume.GetID()
    if labelNumber:
        parameters['labelNumber'] = int(labelNumber[0]) # have to grab first value of tuple for optional argument

    # Rn the smoothing segmentation module from CLI
    cliNode = slicer.cli.run(slicer.modules.segmentationsmoothing, None, parameters, wait_for_completion = True)

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def ResampleVolumefromReference(self, referenceVolume, *inputVolumes):
    """ Resamples an input volume to match ARFI reference volume spacing, size, orientation, and origin
    """
    # Print to Slicer CLI
    print('Resampling volumes to match ARFI...'),
    start_time = time.time()

    for inputVolume in inputVolumes:
        # Run Resample ScalarVectorDWIVolume Module from CLI
        cliParams = {'inputVolume': inputVolume.GetID(), 'outputVolume': inputVolume.GetID(), 'referenceVolume': referenceVolume.GetID()}
        cliNode = slicer.cli.run(slicer.modules.resamplescalarvectordwivolume, None, cliParams, wait_for_completion=True)

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def LabelMapSmoothing(self, inputVolume, Sigma, *labelNumber):
    """ Smooths an input volume labelmap using value of sigma provided (number from 0-5). Optionally smooths only selected labels if more arguments passed
    """
    # Print to Slicer CLI
    print('Additional Label Map Smoothing...'),
    start_time = time.time()

    # Run the slicer module in CLI
    cliParams = {'inputVolume': inputVolume.GetID(), 'outputVolume': inputVolume.GetID(), 'gaussianSigma': Sigma} # input and output defined as same
    if labelNumber:
        cliParams["labelToSmooth"] = labelNumber

    cliNode = slicer.cli.run(slicer.modules.labelmapsmoothing, None, cliParams, wait_for_completion=True)
    
    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def ThresholdScalarVolume(self, inputVolume, newLabelVal):
    """ Thresholds nonzero values on an input labelmap volume to the newLabelVal number while leaving all 0 values untouched
    """
    # Print to Slicer CLI
    print('Changing Label Value...'),
    start_time = time.time()

    # Run the slicer module in CLI
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': inputVolume.GetID(), 'ThresholdType': 'Above', 'ThresholdValue': 0.5, 'OutsideValue': newLabelVal} 
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)
    
    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def RemoveNode(self, *NodestoRemove):
    """ Removes all nodes passed as arguments
    """
    # Print to Slicer CLI
    print('Removing unnecessary nodes from MRML scene...'),
    start_time = time.time()

    # Cycle to remove input nodes
    for node in NodestoRemove:
        slicer.mrmlScene.RemoveNode(node)

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)
 
  def CreateRegistrationLabel(self, inputCapsule, inputCG, inputVM, registerLabel):

    # Print to Slicer CLI
    print('Creating Registration Label...'),
    start_time = time.time()

    # Change Label Values for processing
    self.ThresholdScalarVolume(inputCapsule,  1) 
    self.ThresholdScalarVolume(inputCG,       2)
    self.ThresholdScalarVolume(inputVM,       3)

    # Combine CG and Capsule Labelmaps
    self.ImageLabelCombine(inputCG, inputCapsule, registerLabel) # first label overwrites second

    # # Threshold out areas of only CG and areas of CG/capsule overlap to get only PZ
    self.ThresholdAbove(registerLabel, 1.5, 0) # PZ has value of 1

    # # Threshold VM to 1 before adding
    self.ThresholdAbove(inputVM, 0.5, 1) #(input volume, new label value for nonzero pixels)

    # # Add VM to output Label
    self.ImageLabelCombine(registerLabel, inputVM, registerLabel) # first label overwrites 2nd label

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def ImageLabelCombine(self, inputLabelA, inputLabelB, outputLabel):
    """ Combines labelmaps with label A overwriting label B if any overlapping area
    """
    # Print to Slicer CLI
    print('Combining Labels...'),
    start_time = time.time()

    # Run the slicer module in CLI
    cliParams = {'InputLabelMap_A': inputLabelA.GetID(),'InputLabelMap_B': inputLabelB.GetID(), 'OutputLabelMap': outputLabel.GetID()} 
    cliNode = slicer.cli.run(slicer.modules.imagelabelcombine, None, cliParams, wait_for_completion=True)
    
    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def ThresholdAbove(self, inputVolume, thresholdVal, newLabelVal):
    """ Thresholds nonzero values on an input labelmap volume to the newLabelVal number while leaving all 0 values untouched
    """
    # Print to Slicer CLI
    print('Thresholding Label Value...'),
    start_time = time.time()

    # Run the slicer module in CLI
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': inputVolume.GetID(), 'ThresholdType': 'Above', 'ThresholdValue': thresholdVal, 'OutsideValue': newLabelVal} 
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)
    
    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def MRVMLabelValueProcess(self, inputVolume):
    """ Inverts zero and nonzero label values for a labelmap """
    # Print to Slicer CLI
    print('Thresholding Label Value...'),
    start_time = time.time()

    # Turn zero values into 3
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': inputVolume.GetID(), 'ThresholdType': 'Above', 'ThresholdValue': 0.5, 'OutsideValue': 3, 'Negate': True} 
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # Turn values of above 5 into 0
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': inputVolume.GetID(), 'ThresholdType': 'Above', 'ThresholdValue': 5, 'OutsideValue': 0} 
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)
    
    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def SaveUSRegistrationInputs(self, PatientNumber, inputARFI,  inputBmode,  inputCC, outputUSCaps_Seg,  outputUSCG_Seg, outputUSVM_Seg, outputUSIndex_Seg, outputUSRegister_Label):
    """ Saves Ultrasound volumes and labelmaps after preprocessing prior to registration
    """
    # Print to Slicer CLI
    print('Saving Ultrasound Results...'),
    start_time = time.time()

    # Define filepath    
    root = '/luscinia/ProstateStudy/invivo/Patient'
    inputspath = '/Registration/RegistrationInputs/'

    # Save Ultrasound Files
    slicer.util.saveNode(inputARFI,              (root+PatientNumber+inputspath+'us_ARFI.nii'))
    slicer.util.saveNode(inputBmode,             (root+PatientNumber+inputspath+'us_Bmode.nii'))
    slicer.util.saveNode(inputCC,                (root+PatientNumber+inputspath+'us_ARFICCMask.nrrd'))
    slicer.util.saveNode(outputUSCaps_Seg,       (root+PatientNumber+inputspath+'us_cap-label.nrrd'))
    slicer.util.saveNode(outputUSCG_Seg,         (root+PatientNumber+inputspath+'us_cg-label.nrrd'))
    slicer.util.saveNode(outputUSVM_Seg,         (root+PatientNumber+inputspath+'us_urethra-label.nrrd'))
    slicer.util.saveNode(outputUSIndex_Seg,      (root+PatientNumber+inputspath+'us_indexlesion-label.nrrd'))
    slicer.util.saveNode(outputUSRegister_Label, (root+PatientNumber+inputspath+'us_registration-label.nrrd'))

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

    # Return time elapsed
    return float(end_time-start_time)

  def SaveMRRegistrationInputs(self, PatientNumber, inputT2, outputMRCaps_Seg, outputMRCG_Seg, outputMRVM_Seg, outputMRIndex_Seg, outputMRRegister_Label):
    """ Saves MRI volumes and labelmaps after preprocessing prior to registration
    """
    # Print to Slicer CLI
    print('Saving MRI Results...'),
    start_time = time.time()

    # Define filepath    
    root = '/luscinia/ProstateStudy/invivo/Patient'
    inputspath = '/Registration/RegistrationInputs/'

    # Save MRI Files
    slicer.util.saveNode(inputT2,                (root+PatientNumber+inputspath+'mr_T2_AXIAL.nii'))
    slicer.util.saveNode(outputMRCaps_Seg,       (root+PatientNumber+inputspath+'mr_cap-label.nrrd'))
    slicer.util.saveNode(outputMRCG_Seg,         (root+PatientNumber+inputspath+'mr_cg-label.nrrd'))
    slicer.util.saveNode(outputMRVM_Seg,         (root+PatientNumber+inputspath+'mr_urethra-label.nrrd'))
    slicer.util.saveNode(outputMRIndex_Seg,      (root+PatientNumber+inputspath+'mr_indexlesion-label.nrrd'))
    slicer.util.saveNode(outputMRRegister_Label, (root+PatientNumber+inputspath+'mr_registration-label.nrrd'))


    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

    # Return time elapsed
    return float(end_time-start_time)

  def loadUSInputs(self,PatientNumber):
    """ Loads Ultrasound inputs from designated location on luscinia to nodes in the scene. If inputs are not present, saves node variable as a string with missing filepath for error output
    """

    # Print to Slicer CLI
    print('Loading Ultrasound Inputs...'),
    start_time = time.time()

    if slicer.util.loadVolume('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/slicer/ARFI_Norm_HistEq.nii.gz'):
        inputARFI = slicer.util.getNode('ARFI_Norm_HistEq')
    else:
        inputARFI = '/invivo/Patient'+PatientNumber+'/slicer/ARFI_Norm_HistEq.nii.gz'

    if slicer.util.loadVolume('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/slicer/Bmode.nii.gz'):
        inputBmode = slicer.util.getNode('Bmode')
    else: 
        inputBmode = '/invivo/Patient'+PatientNumber+'/slicer/Bmode.nii.gz'

    if slicer.util.loadLabelVolume('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/slicer/ARFI_CC_Mask.nii.gz'):
        inputCC = slicer.util.getNode('ARFI_CC_Mask')
    else:
        inputCC = '/invivo/Patient'+PatientNumber+'/slicer/ARFI_CC_Mask.nii.gz'

    if slicer.util.loadModel('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/slicer/us_cap.vtk'):
        inputUSCaps_Model = slicer.util.getNode('us_cap')
    else:
        inputUSCaps_Model = '/invivo/Patient'+PatientNumber+'/slicer/us_cap.vtk'

    if slicer.util.loadModel('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/slicer/us_cg.vtk'):
        inputUSCG_Model = slicer.util.getNode('us_cg')
    else:
        inputUSCG_Model = '/invivo/Patient'+PatientNumber+'/slicer/us_cg.vtk'

    if slicer.util.loadModel('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/slicer/us_urethra.vtk'):
        inputUSVM_Model = slicer.util.getNode('us_urethra')
    else:
        inputUSVM_Model = '/invivo/Patient'+PatientNumber+'/slicer/us_urethra.vtk'

    if slicer.util.loadModel('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/slicer/us_lesion1.vtk'):
        inputUSIndex_Model = slicer.util.getNode('us_lesion1')
    else:
        inputUSIndex_Model = '/invivo/Patient'+PatientNumber+'/slicer/us_lesion1.vtk'

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

    return inputARFI, inputBmode, inputCC, inputUSCaps_Model, inputUSCG_Model, inputUSVM_Model, inputUSIndex_Model

  def loadMRInputs(self,PatientNumber):
    """ Loads Ultrasound inputs from designated location on luscinia to nodes in the scene
    """

    # Print to Slicer CLI
    print('Loading MRI Inputs...'),
    start_time = time.time()

    if slicer.util.loadVolume('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/MRI_Images/T2/P'+PatientNumber+'_no_PHI.nii.gz'):
        inputT2 = slicer.util.getNode('P'+PatientNumber+'_no_PHI')
    else:
        inputT2 = '/invivo/Patient'+PatientNumber+'/MRI_Images/T2/P'+PatientNumber+'_no_PHI.nii.gz'

    if slicer.util.loadLabelVolume('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/MRI_Images/P'+PatientNumber+'_segmentation_final.nrrd'):
        inputMRCaps_Seg = slicer.util.getNode('P'+PatientNumber+'_segmentation_final')
    else:
        inputMRCaps_Seg = '/invivo/Patient'+PatientNumber+'/MRI_Images/P'+PatientNumber+'_segmentation_final.nrrd'

    if slicer.util.loadLabelVolume('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/MRI_Images/Anatomy/P'+PatientNumber+'_zones_seg.nii.gz'):
        inputMRZones_Seg = slicer.util.getNode('P'+PatientNumber+'_zones_seg')
    else:
        inputMRZones_Seg = '/invivo/Patient'+PatientNumber+'/MRI_Images/Anatomy/P'+PatientNumber+'_zones_seg.nii.gz'

    if slicer.util.loadLabelVolume('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/MRI_Images/Anatomy/P'+PatientNumber+'_urethra_seg.nrrd'):
        inputMRVM_Seg = slicer.util.getNode('P'+PatientNumber+'_urethra_seg')
    else:
        inputMRVM_Seg = '/invivo/Patient'+PatientNumber+'/MRI_Images/Anatomy/P'+PatientNumber+'_urethra_seg.nrrd'

    if slicer.util.loadLabelVolume('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/MRI_Images/Cancer/P'+PatientNumber+'_lesion1_seg.nrrd'):
        inputMRIndex_Seg = slicer.util.getNode('P'+PatientNumber+'_lesion1_seg')
    else:
        inputMRIndex_Seg = '/invivo/Patient'+PatientNumber+'/MRI_Images/Cancer/P'+PatientNumber+'_lesion1_seg.nrrd'

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

    return inputT2, inputMRCaps_Seg, inputMRZones_Seg, inputMRVM_Seg, inputMRIndex_Seg
  
  def CreateNewLabelVolume(self,name):
    """ Creates a new labelmap volume with the inputted name
    """

    # Create labelmap node
    labelNode=slicer.vtkMRMLLabelMapVolumeNode()
    labelNode.SetName(name)

    # Add volume to scene
    slicer.mrmlScene.AddNode(labelNode)
    displayNode=slicer.vtkMRMLScalarVolumeDisplayNode()
    slicer.mrmlScene.AddNode(displayNode)
    colorNode = slicer.util.getNode('Grey')
    displayNode.SetAndObserveColorNodeID(colorNode.GetID())
    labelNode.SetAndObserveDisplayNodeID(displayNode.GetID())
    labelNode.CreateDefaultStorageNode() 

    return labelNode

  def createUSOutputs(self):
    """ Preallocates output labelmaps with correct names for US
    """

    # Print to Slicer CLI
    print('Preallocating Ultrasound Outputs...'),
    start_time = time.time()

    outputUSCaps_Seg =       self.CreateNewLabelVolume('us_cap-label')
    outputUSCG_Seg =         self.CreateNewLabelVolume('us_cg-label')
    outputUSVM_Seg =         self.CreateNewLabelVolume('us_urethra-label')
    outputUSIndex_Seg =      self.CreateNewLabelVolume('us_indexlesion-label')
    outputUSRegister_Label = self.CreateNewLabelVolume('us_registration-label')

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

    return outputUSCaps_Seg, outputUSCG_Seg, outputUSVM_Seg, outputUSIndex_Seg, outputUSRegister_Label

  def createMROutputs(self):
    """ Preallocates output labelmaps with correct names for MR
    """

    # Print to Slicer CLI
    print('Preallocating MRI Outputs...'),
    start_time = time.time()

    outputMRCaps_Seg =       self.CreateNewLabelVolume('mr_cap-label')
    outputMRCG_Seg =         self.CreateNewLabelVolume('mr_cg-label')
    outputMRVM_Seg =         self.CreateNewLabelVolume('mr_urethra-label')
    outputMRIndex_Seg =      self.CreateNewLabelVolume('mr_indexlesion-label')
    outputMRRegister_Label = self.CreateNewLabelVolume('mr_registration-label')

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

    return outputMRCaps_Seg, outputMRCG_Seg, outputMRVM_Seg, outputMRIndex_Seg, outputMRRegister_Label

  def CheckAllInputsPresent(self, *inputNodes):
    """ Checks if input nodes present and if not returns false
    """
    i = 0 # i stays at 0 if all inputs loaded
    for inputNode in inputNodes:
        if isinstance(inputNode, str):
            print "Input not present: ",
            print inputNode
            i = i+1 # increase i if not all nodes loaded

    if i == 0:
        return True
    else:
        return False


  def run(self, PatientNumber, SaveDataBool):
  #"""
  #      inputARFI,   inputBmode,  inputCC,  inputUSCaps_Model, inputUSCG_Model, inputUSVM_Model,  inputUSIndex_Model,
  #                                          outputUSCaps_Seg,  outputUSCG_Seg,  outputUSVM_Seg,   outputUSIndex_Seg,  outputUSRegister_Label,
  #      inputT2,  inputMRCaps_Seg,  inputMRZones_Seg,  inputMRVM_Seg,  inputMRIndex_Seg, 
  #                outputMRCaps_Seg, outputMRCG_Seg,    outputMRVM_Seg, outputMRIndex_Seg, outputMRRegister_Label):"""
    """
    Run the actual algorithm
    """

    # Print to Slicer CLI
    logging.info('\n\nProcessing started')
    start_time_overall = time.time() # start timer
    print('Expected Algorithm Time: 270 seconds') # based on previous trials of the algorithm

    # Load Ultrasound Inputs
    inputARFI, inputBmode, inputCC, inputUSCaps_Model, inputUSCG_Model, inputUSVM_Model, inputUSIndex_Model = self.loadUSInputs(PatientNumber)

    # Create Ultrasound Outputs
    outputUSCaps_Seg, outputUSCG_Seg, outputUSVM_Seg, outputUSIndex_Seg, outputUSRegister_Label = self.createUSOutputs()
    
    # Load MRI Inputs
    inputT2, inputMRCaps_Seg, inputMRZones_Seg, inputMRVM_Seg, inputMRIndex_Seg = self.loadMRInputs(PatientNumber)

    # Create MR Outputs
    outputMRCaps_Seg, outputMRCG_Seg, outputMRVM_Seg, outputMRIndex_Seg, outputMRRegister_Label = self.createMROutputs()

    # Check if all inputs present
    if not self.CheckAllInputsPresent(inputARFI, inputBmode, inputCC, inputUSCaps_Model, inputUSCG_Model, inputUSVM_Model, inputUSIndex_Model, 
                                      inputT2,  inputMRCaps_Seg,  inputMRZones_Seg,  inputMRVM_Seg,  inputMRIndex_Seg):
        print "Exiting process. Not all inputs supplied."
        return
    
    # Center all of the volume inputs
    self.CenterVolume(inputARFI, inputBmode, inputCC, inputT2,  inputMRCaps_Seg,  inputMRZones_Seg,  inputMRVM_Seg, inputMRIndex_Seg)

    # # Transform all US inputs using inversion transform
    self.US_transform(inputARFI,   inputBmode,  inputCC,  inputUSCaps_Model, inputUSCG_Model, inputUSVM_Model,  inputUSIndex_Model)

    # Smooth MR Final Segmentation to turn into single labelmap of capsule
    self.SegmentationSmoothing(inputMRCaps_Seg, inputMRCaps_Seg)
    
    # Make Model of MRI input capsule segmentation using Model Maker Module for MRI translation coordinates
    intermediateMRCaps_Model = self.MRCapModelMaker(inputMRCaps_Seg)

    # # Transform MRI inputs to match Ultrasound so that MR capsule fits in US volume prior to registration
    self.MR_translate(intermediateMRCaps_Model, inputUSCaps_Model, inputT2,  inputMRCaps_Seg,  inputMRZones_Seg,  inputMRVM_Seg,  inputMRIndex_Seg) # add more MRI inputs to the function

    # Make models of MRI index lesion and veramontanum
    inputMRIndex_Model = self.MRModelMaker(inputMRIndex_Seg, 20) # smooth 20
    inputMRVM_Model    = self.MRModelMaker(inputMRVM_Seg,    30) # smooth 30

    # Convert US Capsule and CG models to labelmap on T2 volume (use T2 for faster conversion since larger image spacing)
    self.ModelToLabelMap(inputT2, inputUSCaps_Model, outputUSCaps_Seg, 0.25)
    self.ModelToLabelMap(inputT2, inputUSCG_Model, outputUSCG_Seg, 0.25)

    # Use Segmentation Smoothing Module on US and MRI Capsule and US CG labels
    self.SegmentationSmoothing(outputUSCaps_Seg, outputUSCaps_Seg) # (inputVolume, outputVolume)
    self.SegmentationSmoothing(outputUSCG_Seg,   outputUSCG_Seg) # define input and output as same volume to keep segmentation applied to output
    self.SegmentationSmoothing(inputMRCaps_Seg,  outputMRCaps_Seg)

    # Use Segmentation Smoothing on MRI zones seg to pick out and smooth only central gland values
    self.SegmentationSmoothing(inputMRZones_Seg, outputMRCG_Seg, 9) # label value 9

    # Resample all segmentations and volumes to match ARFI spacing, size, orientation, origin
    self.ResampleVolumefromReference(inputARFI, outputUSCaps_Seg, outputUSCG_Seg, outputMRCaps_Seg, outputMRCG_Seg, inputT2)

    # Additional smoothing of output labelmaps in label map smoothing module using sigma = 3 (SlicerProstate manuscript)
    self.LabelMapSmoothing(outputUSCaps_Seg, 1) #(input/output volume, sigma for gaussian smoothing, [label to smooth-optional])
    self.LabelMapSmoothing(outputUSCG_Seg,   1)
    self.LabelMapSmoothing(outputMRCaps_Seg, 1)
    self.LabelMapSmoothing(outputMRCG_Seg,   1)

    # Model to labelmap for veramontanum models (** LONG STEP **)
    self.ModelToLabelMap(inputARFI, inputUSVM_Model, outputUSVM_Seg, 0.1)
    self.ModelToLabelMap(inputARFI, inputMRVM_Model, outputMRVM_Seg, 0.1)

    # Model to labelmap for tumor models for ARFI and MRI (** LONG STEP **)
    self.ModelToLabelMap(inputARFI, inputUSIndex_Model, outputUSIndex_Seg, 0.1)
    self.ModelToLabelMap(inputARFI, inputMRIndex_Model, outputMRIndex_Seg, 0.1)

    # Change Label Value for MRI registration label
    # self.MRVMLabelValueProcess(outputMRVM_Seg)
    
    ### Change label map values for output labels before saving
    # For Ultrasound
    self.ThresholdScalarVolume(outputUSCaps_Seg,  1)  #(input volume, new label value for nonzero pixels) # 1 for Capsule
    self.ThresholdScalarVolume(outputUSCG_Seg,    2)  # 2 is CG label
    self.ThresholdScalarVolume(outputUSVM_Seg,    3)  # 3 for VM
    self.ThresholdScalarVolume(outputUSIndex_Seg, 34) # 34 for index tumor
    self.ThresholdScalarVolume(inputCC,         255) # 255 for CC Mask label

    # For MRI
    self.ThresholdScalarVolume(outputMRCaps_Seg,  1)  # 1 for MRI Capsule
    self.ThresholdScalarVolume(outputMRCG_Seg,    2)  # 2 is CG label
    self.ThresholdScalarVolume(outputMRVM_Seg,    3)  # 3 for VM
    self.ThresholdScalarVolume(outputMRIndex_Seg, 34) # 34 for index tumor

    # Create output registration labelmap for MR and US combining Capsule, CG, and VM labelmaps
    self.CreateRegistrationLabel(outputUSCaps_Seg, outputUSCG_Seg, outputUSVM_Seg, outputUSRegister_Label) # for ultrasound
    self.CreateRegistrationLabel(outputMRCaps_Seg, outputMRCG_Seg, outputMRVM_Seg, outputMRRegister_Label) # for ultrasound

    # Change label value for registration labels
    self.ThresholdScalarVolume(outputUSRegister_Label, 10) # 10 for registration label
    self.ThresholdScalarVolume(outputMRRegister_Label, 10) # 10 for registration label

    # Save data if user specifies and figure out time required to save data
    if SaveDataBool:
        US_savetime = self.SaveUSRegistrationInputs(PatientNumber, inputARFI,   inputBmode,  inputCC, outputUSCaps_Seg, outputUSCG_Seg, outputUSVM_Seg, outputUSIndex_Seg, outputUSRegister_Label)
        MR_savetime = self.SaveMRRegistrationInputs(PatientNumber, inputT2,                           outputMRCaps_Seg, outputMRCG_Seg, outputMRVM_Seg, outputMRIndex_Seg, outputMRRegister_Label)
        total_savetime = US_savetime + MR_savetime
    else:
        total_savetime = 0
        
    # Print Completion Status to Slicer CLI
    end_time_overall = time.time()
    logging.info('Processing completed')
    print('Overall Algorithm Time: % 0.1f seconds') % float(end_time_overall-start_time_overall-total_savetime)
    if SaveDataBool:
        print('Overall Saving Time: % 0.1f seconds') % float(total_savetime)
    print('Overall Elapsed Time: % 0.1f seconds') % float(end_time_overall-start_time_overall)

    return True

class PreProcessTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_PreProcess1()

  def test_PreProcess1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = PreProcessLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')