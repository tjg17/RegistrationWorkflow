import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# UltrasoundProcess
#

class UltrasoundProcess(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UltrasoundProcess" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Registration"]
    self.parent.dependencies = []
    self.parent.contributors = ["Tyler Glass (Nightingale Lab)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# UltrasoundProcessWidget
#

class UltrasoundProcessWidget(ScriptedLoadableModuleWidget):
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
    # input ultrasound volume selector
    #
    self.inputSelector1 = slicer.qMRMLNodeComboBox()
    self.inputSelector1.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector1.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.inputSelector1.selectNodeUponCreation = True
    self.inputSelector1.addEnabled = False
    self.inputSelector1.removeEnabled = False
    self.inputSelector1.noneEnabled = False
    self.inputSelector1.showHidden = False
    self.inputSelector1.showChildNodeTypes = False
    self.inputSelector1.setMRMLScene( slicer.mrmlScene )
    self.inputSelector1.setToolTip( "Select Ultrasound Volume (ARFI/Bmode)." )
    parametersFormLayout.addRow("Input U/S Volume: ", self.inputSelector1)

    #
    # input ultrasound capsule VTK model
    #
    self.inputSelector2 = slicer.qMRMLNodeComboBox()
    self.inputSelector2.nodeTypes = ( ("vtkMRMLModelNode"), "" )
    self.inputSelector2.selectNodeUponCreation = True
    self.inputSelector2.addEnabled = False
    self.inputSelector2.removeEnabled = False
    self.inputSelector2.noneEnabled = False
    self.inputSelector2.showHidden = False
    self.inputSelector2.showChildNodeTypes = False
    self.inputSelector2.setMRMLScene( slicer.mrmlScene )
    self.inputSelector2.setToolTip( "Select Ultrasound Model." )
    parametersFormLayout.addRow("Input U/S Model: ", self.inputSelector2)

    #
    # output imaging volume selector
    #
    self.outputSelector1 = slicer.qMRMLNodeComboBox()
    self.outputSelector1.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.outputSelector1.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.outputSelector1.selectNodeUponCreation = True
    self.outputSelector1.addEnabled = True
    self.outputSelector1.removeEnabled = True
    self.outputSelector1.noneEnabled = True
    self.outputSelector1.showHidden = False
    self.outputSelector1.showChildNodeTypes = False
    self.outputSelector1.setMRMLScene( slicer.mrmlScene )
    self.outputSelector1.setToolTip( "Pick output imaging volume." )
    parametersFormLayout.addRow("Output Imaging Volume: ", self.outputSelector1)

    #
    # output segmentation selector
    #
    self.outputSelector2 = slicer.qMRMLNodeComboBox()
    self.outputSelector2.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.outputSelector2.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 ) # this one is a labelmap
    self.outputSelector2.selectNodeUponCreation = True
    self.outputSelector2.addEnabled = True
    self.outputSelector2.removeEnabled = True
    self.outputSelector2.noneEnabled = True
    self.outputSelector2.showHidden = False
    self.outputSelector2.showChildNodeTypes = False
    self.outputSelector2.setMRMLScene( slicer.mrmlScene )
    self.outputSelector2.setToolTip( "Pick output segmentation volume." )
    parametersFormLayout.addRow("Output Segmentation: ", self.outputSelector2)

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
    self.applyButton.enabled = self.inputSelector1.currentNode() and self.inputSelector2.currentNode() # why doesn't this work when I add output volume?

  def onApplyButton(self):
    logic = UltrasoundProcessLogic()
    logic.run(self.inputSelector1.currentNode(), self.inputSelector2.currentNode(), self.outputSelector1.currentNode(), self.outputSelector2.currentNode())

#
# UltrasoundProcessLogic
#

class UltrasoundProcessLogic(ScriptedLoadableModuleLogic):
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

  def isValidInputOutputData(self, inputVolumeNode1, inputModelNode, outputVolumeNode1, outputVolumeNode2):
    """Validates if the output is not the same as input
    """
    if not (inputVolumeNode1 or inputModelNode):
      logging.debug('isValidInputOutputData failed: not all input nodes defined')
      return False
    if not (outputVolumeNode1 or outputVolumeNode2):
      logging.debug('isValidInputOutputData failed: not all output nodes defined')
      return False
    if inputVolumeNode1.GetID()==outputVolumeNode2.GetID() :
      logging.debug('isValidInputOutputData failed: input volume and output segmentation is the same. Create a new segmentation volume for output to avoid this error.')
      return False
    return True

  def run(self, inputVolume, inputModel, outputVolume, outputSegment):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, inputModel, outputVolume, outputSegment):
      slicer.util.errorDisplay('Check that Inputs and Outputs are defined correctly.')
      return False

    logging.info('Processing started')

    # Use "Model to Label Map" module to convert from ultrasound segmented model to segmented label map
    cliParams = {'InputVolume': inputVolume.GetID(), 'surface': inputModel.GetID(), 'OutputVolume': outputSegment.GetID(), 'sampleDistance': 0.1, 'labelValue': 10}
    cliNode = slicer.cli.run(slicer.modules.modeltolabelmap, None, cliParams, wait_for_completion=True)

    # Transform US volume and segmentation labelmap using [ 0 0 -1 0 ] linear transform (flips apex/base but maintains left/right)
    # define inversion transform (currently have this as saved in filesystem, want to create it in the code)
    invert_transform = slicer.util.loadTransform('/home/tjg17/SlicerPython/invert_transform.h5') # Want to make this more robust so not dependent on filesystem
    # Run the resample scalar/vector/DWI volume module to create new output volumes
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'transformationFile': 'invert_transform.h5'}
    cliNode = slicer.cli.run(slicer.modules.resamplescalarvectordwivolume, None, cliParams, wait_for_completion=True)
    # Resample labelmap
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputSegment.GetID(), 'transformationFile': 'invert_transform.h5'}
    cliNode = slicer.cli.run(slicer.modules.resamplescalarvectordwivolume, None, cliParams, wait_for_completion=True)


    logging.info('Processing completed')

    return True


#
# Still need to make tests
#

class UltrasoundProcessTest(ScriptedLoadableModuleTest):
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
    self.test_UltrasoundProcess1()

  def test_UltrasoundProcess1(self):
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
    logic = UltrasoundProcessLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
