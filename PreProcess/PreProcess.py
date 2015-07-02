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

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Ultrasound Data"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input ARFI volume selector
    #
    self.USinputSelector1 = slicer.qMRMLNodeComboBox()
    self.USinputSelector1.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.USinputSelector1.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.USinputSelector1.selectNodeUponCreation = True
    self.USinputSelector1.addEnabled = False
    self.USinputSelector1.removeEnabled = False
    self.USinputSelector1.noneEnabled = False
    self.USinputSelector1.showHidden = False
    self.USinputSelector1.showChildNodeTypes = False
    self.USinputSelector1.setMRMLScene( slicer.mrmlScene )
    self.USinputSelector1.setToolTip( "Select ARFI_Norm_HistEq.nii.gz volume." )
    parametersFormLayout.addRow("Input ARFI Volume: ", self.USinputSelector1)

    #
    # input Bmode volume selector
    #
    self.USinputSelector2 = slicer.qMRMLNodeComboBox()
    self.USinputSelector2.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.USinputSelector2.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.USinputSelector2.selectNodeUponCreation = True
    self.USinputSelector2.addEnabled = False
    self.USinputSelector2.removeEnabled = False
    self.USinputSelector2.noneEnabled = False
    self.USinputSelector2.showHidden = False
    self.USinputSelector2.showChildNodeTypes = False
    self.USinputSelector2.setMRMLScene( slicer.mrmlScene )
    self.USinputSelector2.setToolTip( "Select Bmode.nii.gz volume." )
    parametersFormLayout.addRow("Input Bmode Volume: ", self.USinputSelector2)

    #
    # input CC Mask label volume selector
    #
    self.USinputSelector3 = slicer.qMRMLNodeComboBox()
    self.USinputSelector3.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.USinputSelector3.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 )
    self.USinputSelector3.selectNodeUponCreation = True
    self.USinputSelector3.addEnabled = False
    self.USinputSelector3.removeEnabled = False
    self.USinputSelector3.noneEnabled = False
    self.USinputSelector3.showHidden = False
    self.USinputSelector3.showChildNodeTypes = False
    self.USinputSelector3.setMRMLScene( slicer.mrmlScene )
    self.USinputSelector3.setToolTip( "Select ARFI_CC_Mask.nii.gz volume." )
    parametersFormLayout.addRow("Input ARFI CC Mask: ", self.USinputSelector3)

    #
    # input ultrasound capsule VTK model
    #
    self.USinputSelector4 = slicer.qMRMLNodeComboBox()
    self.USinputSelector4.nodeTypes = ( ("vtkMRMLModelNode"), "" )
    self.USinputSelector4.selectNodeUponCreation = True
    self.USinputSelector4.addEnabled = False
    self.USinputSelector4.removeEnabled = False
    self.USinputSelector4.noneEnabled = False
    self.USinputSelector4.showHidden = False
    self.USinputSelector4.showChildNodeTypes = False
    self.USinputSelector4.setMRMLScene( slicer.mrmlScene )
    self.USinputSelector4.setToolTip( "Select us_cap.vtk model." )
    parametersFormLayout.addRow("Input U/S Capsule Model: ", self.USinputSelector4)

    #
    # input ultrasound central gland VTK model
    #
    self.USinputSelector5 = slicer.qMRMLNodeComboBox()
    self.USinputSelector5.nodeTypes = ( ("vtkMRMLModelNode"), "" )
    self.USinputSelector5.selectNodeUponCreation = True
    self.USinputSelector5.addEnabled = False
    self.USinputSelector5.removeEnabled = False
    self.USinputSelector5.noneEnabled = False
    self.USinputSelector5.showHidden = False
    self.USinputSelector5.showChildNodeTypes = False
    self.USinputSelector5.setMRMLScene( slicer.mrmlScene )
    self.USinputSelector5.setToolTip( "Select us_cg.vtk model." )
    parametersFormLayout.addRow("Input U/S Central Gland Model: ", self.USinputSelector5)

    #
    # input ultrasound veramontanum VTK model
    #
    self.USinputSelector51 = slicer.qMRMLNodeComboBox()
    self.USinputSelector51.nodeTypes = ( ("vtkMRMLModelNode"), "" )
    self.USinputSelector51.selectNodeUponCreation = True
    self.USinputSelector51.addEnabled = False
    self.USinputSelector51.removeEnabled = False
    self.USinputSelector51.noneEnabled = False
    self.USinputSelector51.showHidden = False
    self.USinputSelector51.showChildNodeTypes = False
    self.USinputSelector51.setMRMLScene( slicer.mrmlScene )
    self.USinputSelector51.setToolTip( "Select us_vm.vtk model." )
    parametersFormLayout.addRow("Input U/S Veramontanum Model: ", self.USinputSelector51)

    #
    # input ultrasound index lesion VTK model
    #
    self.USinputSelector6 = slicer.qMRMLNodeComboBox()
    self.USinputSelector6.nodeTypes = ( ("vtkMRMLModelNode"), "" )
    self.USinputSelector6.selectNodeUponCreation = True
    self.USinputSelector6.addEnabled = False
    self.USinputSelector6.removeEnabled = False
    self.USinputSelector6.noneEnabled = False
    self.USinputSelector6.showHidden = False
    self.USinputSelector6.showChildNodeTypes = False
    self.USinputSelector6.setMRMLScene( slicer.mrmlScene )
    self.USinputSelector6.setToolTip( "Select us_indexlesion.vtk model." )
    parametersFormLayout.addRow("Input U/S Index Lesion Model: ", self.USinputSelector6)

    #
    # output capsule segmentation selector
    #
    self.USoutputSelector1 = slicer.qMRMLNodeComboBox()
    self.USoutputSelector1.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.USoutputSelector1.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 ) # this one is a labelmap
    self.USoutputSelector1.selectNodeUponCreation = True
    self.USoutputSelector1.addEnabled = True
    self.USoutputSelector1.removeEnabled = True
    self.USoutputSelector1.renameEnabled = False
    self.USoutputSelector1.baseName = "us_cap-label"
    self.USoutputSelector1.noneEnabled = False
    self.USoutputSelector1.showHidden = False
    self.USoutputSelector1.showChildNodeTypes = False
    self.USoutputSelector1.setMRMLScene( slicer.mrmlScene )
    self.USoutputSelector1.setToolTip( "Select ""Create new volume""." )
    parametersFormLayout.addRow("Output U/S Capsule Segmentation: ", self.USoutputSelector1)

    #
    # output central gland segmentation selector
    #
    self.USoutputSelector2 = slicer.qMRMLNodeComboBox()
    self.USoutputSelector2.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.USoutputSelector2.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 ) # this one is a labelmap
    self.USoutputSelector2.selectNodeUponCreation = True
    self.USoutputSelector2.addEnabled = True
    self.USoutputSelector2.removeEnabled = True
    self.USoutputSelector2.renameEnabled = False
    self.USoutputSelector2.baseName = "us_cg-label"
    self.USoutputSelector2.noneEnabled = False
    self.USoutputSelector2.showHidden = False
    self.USoutputSelector2.showChildNodeTypes = False
    self.USoutputSelector2.setMRMLScene( slicer.mrmlScene )
    self.USoutputSelector2.setToolTip( "Select ""Create new volume""." )
    parametersFormLayout.addRow("Output U/S Central Gland Segment: ", self.USoutputSelector2)

    #
    # output index lesion segmentation selector
    #
    self.USoutputSelector3 = slicer.qMRMLNodeComboBox()
    self.USoutputSelector3.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.USoutputSelector3.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 ) # this one is a labelmap
    self.USoutputSelector3.selectNodeUponCreation = True
    self.USoutputSelector3.addEnabled = True
    self.USoutputSelector3.removeEnabled = True
    self.USoutputSelector3.renameEnabled = False
    self.USoutputSelector3.baseName = "us_indexlesion-label"
    self.USoutputSelector3.noneEnabled = False
    self.USoutputSelector3.showHidden = False
    self.USoutputSelector3.showChildNodeTypes = False
    self.USoutputSelector3.setMRMLScene( slicer.mrmlScene )
    self.USoutputSelector3.setToolTip( "Select ""Create new volume""." )
    parametersFormLayout.addRow("Output U/S Index Lesion: ", self.USoutputSelector3)

    #
    # output registration label selector
    #
    self.USoutputSelector4 = slicer.qMRMLNodeComboBox()
    self.USoutputSelector4.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.USoutputSelector4.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 ) # this one is a labelmap
    self.USoutputSelector4.selectNodeUponCreation = True
    self.USoutputSelector4.addEnabled = True
    self.USoutputSelector4.removeEnabled = True
    self.USoutputSelector4.renameEnabled = False
    self.USoutputSelector4.baseName = "us_register-label"
    self.USoutputSelector4.noneEnabled = False
    self.USoutputSelector4.showHidden = False
    self.USoutputSelector4.showChildNodeTypes = False
    self.USoutputSelector4.setMRMLScene( slicer.mrmlScene )
    self.USoutputSelector4.setToolTip( "Select ""Create new volume""." )
    parametersFormLayout.addRow("Output U/S Registration Label: ", self.USoutputSelector4)


    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "MRI Data"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input T2 axial volume
    #
    self.MRinputSelector1 = slicer.qMRMLNodeComboBox()
    self.MRinputSelector1.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.MRinputSelector1.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.MRinputSelector1.selectNodeUponCreation = True
    self.MRinputSelector1.addEnabled = False
    self.MRinputSelector1.removeEnabled = False
    self.MRinputSelector1.noneEnabled = False
    self.MRinputSelector1.showHidden = False
    self.MRinputSelector1.showChildNodeTypes = False
    self.MRinputSelector1.setMRMLScene( slicer.mrmlScene )
    self.MRinputSelector1.setToolTip( "Select PXX_no_PHI.nii.gz." )
    parametersFormLayout.addRow("Input T2-MRI Volume: ", self.MRinputSelector1)

    #
    # input T2-MRI capsule dsegmentation
    #
    self.MRinputSelector2 = slicer.qMRMLNodeComboBox()
    self.MRinputSelector2.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.MRinputSelector2.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 )
    self.MRinputSelector2.selectNodeUponCreation = True
    self.MRinputSelector2.addEnabled = False
    self.MRinputSelector2.removeEnabled = False
    self.MRinputSelector2.noneEnabled = False
    self.MRinputSelector2.showHidden = False
    self.MRinputSelector2.showChildNodeTypes = False
    self.MRinputSelector2.setMRMLScene( slicer.mrmlScene )
    self.MRinputSelector2.setToolTip( "Select PXX_segmentation_final.nii.gz." )
    parametersFormLayout.addRow("Input T2-MRI Final Segmentation: ", self.MRinputSelector2)

    #
    # input T2-MRI zones segmentation
    #
    self.MRinputSelector3 = slicer.qMRMLNodeComboBox()
    self.MRinputSelector3.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.MRinputSelector3.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 )
    self.MRinputSelector3.selectNodeUponCreation = True
    self.MRinputSelector3.addEnabled = False
    self.MRinputSelector3.removeEnabled = False
    self.MRinputSelector3.noneEnabled = False
    self.MRinputSelector3.showHidden = False
    self.MRinputSelector3.showChildNodeTypes = False
    self.MRinputSelector3.setMRMLScene( slicer.mrmlScene )
    self.MRinputSelector3.setToolTip( "Select PXX_zones_seg.nii.gz." )
    parametersFormLayout.addRow("Input T2-MRI Zones Segmentation: ", self.MRinputSelector3)

    #
    # input T2-MRI cancer/BPH/overall segmentation
    #
    self.MRinputSelector4 = slicer.qMRMLNodeComboBox()
    self.MRinputSelector4.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.MRinputSelector4.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 )
    self.MRinputSelector4.selectNodeUponCreation = True
    self.MRinputSelector4.addEnabled = False
    self.MRinputSelector4.removeEnabled = False
    self.MRinputSelector4.noneEnabled = False
    self.MRinputSelector4.showHidden = False
    self.MRinputSelector4.showChildNodeTypes = False
    self.MRinputSelector4.setMRMLScene( slicer.mrmlScene )
    self.MRinputSelector4.setToolTip( "Select PXX_lesion1.nrrd." )
    parametersFormLayout.addRow("Input T2-MRI Index Lesion Segmentation: ", self.MRinputSelector4)

    #
    # output capsule segmentation selector
    #
    self.MRoutputSelector2 = slicer.qMRMLNodeComboBox()
    self.MRoutputSelector2.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.MRoutputSelector2.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 ) # this one is a labelmap
    self.MRoutputSelector2.selectNodeUponCreation = True
    self.MRoutputSelector2.addEnabled = True
    self.MRoutputSelector2.removeEnabled = True
    self.MRoutputSelector2.renameEnabled = False
    self.MRoutputSelector2.baseName = "mr_cap-label"
    self.MRoutputSelector2.noneEnabled = False
    self.MRoutputSelector2.showHidden = False
    self.MRoutputSelector2.showChildNodeTypes = False
    self.MRoutputSelector2.setMRMLScene( slicer.mrmlScene )
    self.MRoutputSelector2.setToolTip( "Select ""Create new volume""." )
    parametersFormLayout.addRow("Output T2-MRI Capsule Segmentation: ", self.MRoutputSelector2)

    #
    # output central gland segmentation selector
    #
    self.MRoutputSelector3 = slicer.qMRMLNodeComboBox()
    self.MRoutputSelector3.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.MRoutputSelector3.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 ) # this one is a labelmap
    self.MRoutputSelector3.selectNodeUponCreation = True
    self.MRoutputSelector3.addEnabled = True
    self.MRoutputSelector3.removeEnabled = True
    self.MRoutputSelector3.renameEnabled = False
    self.MRoutputSelector3.baseName = "mr_cg-label"
    self.MRoutputSelector3.noneEnabled = False
    self.MRoutputSelector3.showHidden = False
    self.MRoutputSelector3.showChildNodeTypes = False
    self.MRoutputSelector3.setMRMLScene( slicer.mrmlScene )
    self.MRoutputSelector3.setToolTip( "Select ""Create new volume""." )
    parametersFormLayout.addRow("Output T2-MRI Central Gland Segment: ", self.MRoutputSelector3)

    #
    # output final segmentation (tumors/BPH/etc) selector
    #
    self.MRoutputSelector4 = slicer.qMRMLNodeComboBox()
    self.MRoutputSelector4.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.MRoutputSelector4.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 ) # this one is a labelmap
    self.MRoutputSelector4.selectNodeUponCreation = True
    self.MRoutputSelector4.addEnabled = True
    self.MRoutputSelector4.removeEnabled = True
    self.MRoutputSelector4.renameEnabled = False
    self.MRoutputSelector4.baseName = "mr_indexlesion-label"
    self.MRoutputSelector4.noneEnabled = False
    self.MRoutputSelector4.showHidden = False
    self.MRoutputSelector4.showChildNodeTypes = False
    self.MRoutputSelector4.setMRMLScene( slicer.mrmlScene )
    self.MRoutputSelector4.setToolTip( "Select ""Create new volume""." )
    parametersFormLayout.addRow("Output T2-MRI Index Lesion Segmentation: ", self.MRoutputSelector4)


    #
    # Output Segmentation Params Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Run the Algorithm"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
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
    logic.run(str(int(self.PatientNumberIterationsSpinBox.value)), self.SaveDataCheckBox.checked, 
              self.USinputSelector1.currentNode(),  self.USinputSelector2.currentNode(),  self.USinputSelector3.currentNode(),  self.USinputSelector4.currentNode(),  self.USinputSelector5.currentNode(), self.USinputSelector6.currentNode(),
              self.USoutputSelector1.currentNode(), self.USoutputSelector2.currentNode(), 
              self.MRinputSelector1.currentNode(),  self.MRinputSelector2.currentNode(),  self.MRinputSelector3.currentNode(),  self.MRinputSelector4.currentNode(), 
                                                    self.MRoutputSelector2.currentNode(), self.MRoutputSelector3.currentNode(), self.MRoutputSelector4.currentNode())

#
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

  def ModelToLabelMap(self, inputVolume, inputModel, outputVolume):
    """ Converts models into a labelmap on the input T2-MRI volume using 0.25 sample distance to be smaller than MRI smallest pixel width
    """
    # Print to Slicer CLI
    print('Converting Model to Label Map...'),
    start_time = time.time()

    # Get spacing of inputVolume and multiply by 0.8 to determine sample distance
    samplevoxeldistance = round(0.8*min(inputVolume.GetSpacing()),2) # rounds to 2 decimal points for 80% of smallest voxel

    # Run the slicer module in CLI
    cliParams = {'InputVolume': inputVolume.GetID(), 'surface': inputModel.GetID(), 'OutputVolume': outputVolume.GetID(), 'sampleDistance': samplevoxeldistance, 'labelValue': 10}
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

  def MRTumorModelMaker(self, inputMRlabel):
    """ Converts MRI tumor labelmap segemntation into slicer VTK model node
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
    parameters["Smooth"] = 20
    parameters["Name"] = 'lesion'

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
    outHierarchy.SetName( "Lesion Models" )
    slicer.mrmlScene.AddNode( outHierarchy )

    # Set the parameter for the output model heirarchy
    parameters["ModelSceneFile"] = outHierarchy

    # Run the module from the command line
    slicer.cli.run(slicer.modules.modelmaker, None, parameters, wait_for_completion=True)

    # Define the output model as the created model in the scene
    outputMRModel = slicer.util.getNode('lesion_34_34') # index lesion label has label value of 34 

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

  def SaveUSRegistrationInputs(self, PatientNumber, inputARFI,  inputBmode,  inputCC, outputUSCaps_Seg,  outputUSCG_Seg):
    """ Saves Ultrasound volumes and labelmaps after preprocessing prior to registration
    """
    # Print to Slicer CLI
    print('Saving Ultrasound Results...'),
    start_time = time.time()

    # Define filepath    
    root = '/luscinia/ProstateStudy/invivo/Patient'
    inputspath = '/Registration/RegistrationInputs/'

    # Save Ultrasound Files
    slicer.util.saveNode(inputARFI,        (root+PatientNumber+inputspath+'us_ARFI.nii'))
    slicer.util.saveNode(inputBmode,       (root+PatientNumber+inputspath+'us_Bmode.nii'))
    slicer.util.saveNode(inputCC,          (root+PatientNumber+inputspath+'us_ARFICCMask.nrrd'))
    slicer.util.saveNode(outputUSCaps_Seg, (root+PatientNumber+inputspath+'us_cap-label.nrrd'))
    slicer.util.saveNode(outputUSCG_Seg,   (root+PatientNumber+inputspath+'us_cg-label.nrrd'))

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

    # Return time elapsed
    return float(end_time-start_time)

  def SaveMRRegistrationInputs(self, PatientNumber, inputT2, outputMRCaps_Seg, outputMRCG_Seg, outputMRIndex_Seg):
    """ Saves MRI volumes and labelmaps after preprocessing prior to registration
    """
    # Print to Slicer CLI
    print('Saving MRI Results...'),
    start_time = time.time()

    # Define filepath    
    root = '/luscinia/ProstateStudy/invivo/Patient'
    inputspath = '/Registration/RegistrationInputs/'

    # Save MRI Files
    slicer.util.saveNode(inputT2,            (root+PatientNumber+inputspath+'mr_T2_AXIAL.nii'))
    slicer.util.saveNode(outputMRCaps_Seg,   (root+PatientNumber+inputspath+'mr_cap-label.nrrd'))
    slicer.util.saveNode(outputMRCG_Seg,     (root+PatientNumber+inputspath+'mr_cg-label.nrrd'))
    slicer.util.saveNode(outputMRIndex_Seg,  (root+PatientNumber+inputspath+'mr_indexlesion-label.nrrd'))

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

    # Return time elapsed
    return float(end_time-start_time)

  def saveScene(self, PatientNumber):
    """ Saves MRML scene
    """
    # Print to Slicer CLI
    print('Saving MRML Scene...'),
    start_time = time.time()

    # Define filepath    
    root = '/luscinia/ProstateStudy/invivo/Patient'
    inputspath = '/Registration/RegistrationInputs/'

    # Save MRI Files
    slicer.util.saveScene(root+PatientNumber+inputspath+PatientNumber+'_RegistrationInputScene.mrml')

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

    # Return time elapsed
    return float(end_time-start_time)


  def run(self, PatientNumber, SaveDataBool,
        inputARFI,   inputBmode,  inputCC,  inputUSCaps_Model, inputUSCG_Model, inputUSIndex_Model,
                                            outputUSCaps_Seg,  outputUSCG_Seg, 
        inputT2,  inputMRCaps_Seg,  inputMRZones_Seg,  inputMRIndex_Seg, 
                  outputMRCaps_Seg, outputMRCG_Seg,   outputMRIndex_Seg):
    """
    Run the actual algorithm
    """
    # # Check user-defined inputs and outputs
    # if not self.isValidUltrasoundData(inputARFI, inputBmode, inputUSCaps_Model, outputUSCaps_Seg):
    #   slicer.util.errorDisplay('Check that Ultrasound Inputs/Outputs are correctly defined.')
    #   return False
    # if not self.isValidMRIData(inputT2, inputMRCaps_Seg, outputMRCaps_Seg):
    #   slicer.util.errorDisplay('Check that MRI Inputs/Outputs are correctly defined.')
    #   return False

    # Print to Slicer CLI
    logging.info('\n\nProcessing started')
    start_time_overall = time.time() # start timer
    print('Expected Algorithm Time: 95 seconds') # based on previous trials of the algorithm
    
    # Center all of the volume inputs
    self.CenterVolume(inputARFI, inputBmode, inputCC, inputT2,  inputMRCaps_Seg,  inputMRZones_Seg,  inputMRIndex_Seg)

    # # Transform all US inputs using inversion transform
    self.US_transform(inputARFI, inputBmode, inputCC, inputUSCaps_Model, inputUSCG_Model) 

    # Smooth MR Final Segmentation to turn into single labelmap of capsule
    self.SegmentationSmoothing(inputMRCaps_Seg, inputMRCaps_Seg)
    
    # Make Model of MRI input capsule segmentation using Model Maker Module for MRI translation coordinates
    intermediateMRCaps_Model = self.MRCapModelMaker(inputMRCaps_Seg)

    # # Transform MRI inputs to match Ultrasound so that MR capsule fits in US volume prior to registration
    self.MR_translate(intermediateMRCaps_Model, inputUSCaps_Model, inputT2,  inputMRCaps_Seg,  inputMRZones_Seg,  inputMRIndex_Seg) # add more MRI inputs to the function

    # Make a model of index lesion tumor after changing label value to 34
    self.ThresholdScalarVolume(inputMRIndex_Seg,  34)
    indexlesion_model = self.MRTumorModelMaker(inputMRIndex_Seg)

    # Convert US Capsule and CG models to labelmap on T2 volume (use T2 for faster conversion)
    self.ModelToLabelMap(inputT2, inputUSCaps_Model, outputUSCaps_Seg)
    self.ModelToLabelMap(inputT2, inputUSCG_Model, outputUSCG_Seg)

    # Use Segmentation Smoothing Module on US and MRI Capsule and US CG labels
    self.SegmentationSmoothing(outputUSCaps_Seg, outputUSCaps_Seg) # (inputVolume, outputVolume)
    self.SegmentationSmoothing(outputUSCG_Seg, outputUSCG_Seg) # define input and output as same volume to keep segmentation applied to output
    self.SegmentationSmoothing(inputMRCaps_Seg, outputMRCaps_Seg)

    # Use Segmentation Smoothing on MRI zones seg to pick out and smooth only central gland values
    self.SegmentationSmoothing(inputMRZones_Seg, outputMRCG_Seg, 9) # label value 9

    # Resample all segmentations and volumes to match ARFI spacing, size, orientation, origin
    self.ResampleVolumefromReference(inputARFI, outputUSCaps_Seg, outputUSCG_Seg, outputMRCaps_Seg, outputMRCG_Seg, outputMRIndex_Seg, inputT2)

    # Model to labelmap for tumor model onto resampled MRI (** LONGEST STEP **)
    self.ModelToLabelMap(inputT2, indexlesion_model, outputMRIndex_Seg)

    # Additional smoothing of output labelmaps in label map smoothing module using sigma = 3 (SlicerProstate manuscript)
    self.LabelMapSmoothing(outputUSCaps_Seg, 1) #(input/output volume, sigma for gaussian smoothing, [label to smooth-optional])
    self.LabelMapSmoothing(outputUSCG_Seg,   1)
    self.LabelMapSmoothing(outputMRCaps_Seg, 1)
    self.LabelMapSmoothing(outputMRCG_Seg,   1)

    # Threshold Scalar volume to change label map value for output labels
    self.ThresholdScalarVolume(outputUSCaps_Seg,  1) #(input volume, new label value for nonzero pixels)
    self.ThresholdScalarVolume(outputUSCG_Seg,    2) # 2 is CG label
    self.ThresholdScalarVolume(outputMRCaps_Seg,  1) # 1 is Capsule label
    self.ThresholdScalarVolume(outputMRCG_Seg,    2)
    self.ThresholdScalarVolume(outputMRIndex_Seg, 3) # 3 is index tumor label
    self.ThresholdScalarVolume(inputCC,         255) # 255 for CC Mask label

    # Remove Unused Intermediate Nodes before display
    self.RemoveNode(inputUSCaps_Model, inputUSCG_Model, indexlesion_model)

    # Remove input nodes that are not to be saved
    self.RemoveNode(inputMRCaps_Seg, inputMRZones_Seg,  inputMRIndex_Seg)

    # Save data if user specifies and figure out time required to save data
    if SaveDataBool:
        US_savetime = self.SaveUSRegistrationInputs(PatientNumber, inputARFI,   inputBmode,  inputCC, outputUSCaps_Seg,  outputUSCG_Seg)
        MR_savetime = self.SaveMRRegistrationInputs(PatientNumber, inputT2, outputMRCaps_Seg, outputMRCG_Seg, outputMRIndex_Seg)
        scene_savetime = self.saveScene(PatientNumber)
        total_savetime = US_savetime + MR_savetime + scene_savetime
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