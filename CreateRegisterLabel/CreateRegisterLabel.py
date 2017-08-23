import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import time # for measuring time of processing steps

#
# CreateRegisterLabel
#
# This module can be used to create a registration label prior to registration.
# The preferred way to create a registration label is via PreProcess() module as this will process all U/S and MRI inputs and segmentations.
# This is a legacy module that should not need to be used as its functionality is already in PreProcess module.

class CreateRegisterLabel(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "CreateRegisterLabel" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Prostate"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# CreateRegisterLabelWidget
#

class CreateRegisterLabelWidget(ScriptedLoadableModuleWidget):
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
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input capsule segmentation selector
    #
    self.inputSelector1 = slicer.qMRMLNodeComboBox()
    self.inputSelector1.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector1.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1)
    self.inputSelector1.selectNodeUponCreation = True
    self.inputSelector1.addEnabled = False
    self.inputSelector1.removeEnabled = False
    self.inputSelector1.noneEnabled = False
    self.inputSelector1.showHidden = False
    self.inputSelector1.showChildNodeTypes = False
    self.inputSelector1.setMRMLScene( slicer.mrmlScene )
    self.inputSelector1.setToolTip( "Select Capsule Segmentation." )
    parametersFormLayout.addRow("Capsule: ", self.inputSelector1)

    #
    # input central gland segmentation selector
    #
    self.inputSelector2 = slicer.qMRMLNodeComboBox()
    self.inputSelector2.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector2.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 )
    self.inputSelector2.selectNodeUponCreation = True
    self.inputSelector2.addEnabled = False
    self.inputSelector2.removeEnabled = False
    self.inputSelector2.noneEnabled = False
    self.inputSelector2.showHidden = False
    self.inputSelector2.showChildNodeTypes = False
    self.inputSelector2.setMRMLScene( slicer.mrmlScene )
    self.inputSelector2.setToolTip( "Select Central Gland Segmentation." )
    parametersFormLayout.addRow("Central Gland: ", self.inputSelector2)

    #
    # input Veramontanum segmentation selector
    #
    self.inputSelector3 = slicer.qMRMLNodeComboBox()
    self.inputSelector3.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector3.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 )
    self.inputSelector3.selectNodeUponCreation = True
    self.inputSelector3.addEnabled = False
    self.inputSelector3.removeEnabled = False
    self.inputSelector3.noneEnabled = False
    self.inputSelector3.showHidden = False
    self.inputSelector3.showChildNodeTypes = False
    self.inputSelector3.setMRMLScene( slicer.mrmlScene )
    self.inputSelector3.setToolTip( "Select Veramontanum Segmentation." )
    parametersFormLayout.addRow("Veramontanum: ", self.inputSelector3)

    #
    # output registration segmentation selector
    #
    self.outputSelector1 = slicer.qMRMLNodeComboBox()
    self.outputSelector1.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.outputSelector1.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 ) # this one is a labelmap
    self.outputSelector1.selectNodeUponCreation = True
    self.outputSelector1.addEnabled = True
    self.outputSelector1.removeEnabled = True
    self.outputSelector1.renameEnabled = False
    self.outputSelector1.baseName = "register-label"
    self.outputSelector1.noneEnabled = False
    self.outputSelector1.showHidden = False
    self.outputSelector1.showChildNodeTypes = False
    self.outputSelector1.setMRMLScene( slicer.mrmlScene )
    self.outputSelector1.setToolTip( "Select ""Create new volume""." )
    parametersFormLayout.addRow("Output Segmentation: ", self.outputSelector1)

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

  def cleanup(self):
    pass

  def onApplyButton(self):
    logic = CreateRegisterLabelLogic()
    logic.run(self.inputSelector1.currentNode(), self.inputSelector2.currentNode(), self.inputSelector3.currentNode(), 
              self.outputSelector1.currentNode())

#
# CreateRegisterLabelLogic
#

class CreateRegisterLabelLogic(ScriptedLoadableModuleLogic):
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

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def ThresholdAbove(self, inputVolume, thresholdVal, newLabelVal):
    """ Thresholds nonzero values on an input labelmap volume to the newLabelVal number while leaving all 0 values untouched
    """
    # Print to Slicer CLI
    print('Changing Label Value...'),
    start_time = time.time()

    # Run the slicer module in CLI
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': inputVolume.GetID(), 'ThresholdType': 'Above', 'ThresholdValue': thresholdVal, 'OutsideValue': newLabelVal} 
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)
    
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

  def run(self, inputCapsule, inputCG, inputVM, outputLabel):
    """
    Run the actual algorithm
    """

    # Print to Slicer CLI
    logging.info('\n\nProcessing started')
    start_time_overall = time.time() # start timer

    # Combine CG and Capsule Labelmaps
    self.ImageLabelCombine(inputCG, inputCapsule, outputLabel) 

    # # Threshold out areas of only CG and areas of CG/capsule overlap to get only PZ
    self.ThresholdAbove(outputLabel, 1.5, 0) # PZ has value of 1

    # # Threshold VM to 1 before adding
    self.ThresholdAbove(inputVM, 0.5, 1) #(input volume, new label value for nonzero pixels)

    # # Add VM to output Label
    self.ImageLabelCombine(outputLabel, inputVM, outputLabel) # first label overwrites 2nd label

    # Print to Slicer CLI
    end_time_overall = time.time()
    logging.info('Processing completed')
    print('Overall Algorithm Time: % 0.1f seconds') % float(end_time_overall-start_time_overall)

    return True


class CreateRegisterLabelTest(ScriptedLoadableModuleTest):
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
    self.test_CreateRegisterLabel1()

  def test_CreateRegisterLabel1(self):
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
    logic = CreateRegisterLabelLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
