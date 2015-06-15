import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# T2Process
#

class T2Process(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "T2Process" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Custom"]
    self.parent.dependencies = []
    self.parent.contributors = ["Tyler Glass (Nightingale Lab)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is a scripted loadable module bundled in an extension.
    It performs pre-processing for T2-MRI volumes prior to registration.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# T2ProcessWidget
#

class T2ProcessWidget(ScriptedLoadableModuleWidget):
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
    # input T2 axial volume
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
    self.inputSelector1.setToolTip( "Select axial T2-MRI." )
    parametersFormLayout.addRow("Input T2-MRI Volume: ", self.inputSelector1)

    #
    # input T2-MRI segmentation
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
    self.inputSelector2.setToolTip( "Select axial T2-MRI segmentation." )
    parametersFormLayout.addRow("Input T2-MRI Segment: ", self.inputSelector2)

    #
    # input ultrasound capsule VTK model
    #
    self.inputSelector3 = slicer.qMRMLNodeComboBox()
    self.inputSelector3.nodeTypes = ( ("vtkMRMLModelNode"), "" )
    self.inputSelector3.selectNodeUponCreation = True
    self.inputSelector3.addEnabled = False
    self.inputSelector3.removeEnabled = False
    self.inputSelector3.noneEnabled = False
    self.inputSelector3.showHidden = False
    self.inputSelector3.showChildNodeTypes = False
    self.inputSelector3.setMRMLScene( slicer.mrmlScene )
    self.inputSelector3.setToolTip( "Select Ultrasound Model." )
    parametersFormLayout.addRow("Input U/S Model: ", self.inputSelector3)


    #
    # output segmentation selector
    #
    self.outputSelector1 = slicer.qMRMLNodeComboBox()
    self.outputSelector1.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.outputSelector1.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 ) # this one is a labelmap
    self.outputSelector1.selectNodeUponCreation = True
    self.outputSelector1.addEnabled = True
    self.outputSelector1.removeEnabled = True
    self.outputSelector1.renameEnabled = True
    self.outputSelector1.baseName = "Output Label"
    self.outputSelector1.noneEnabled = True
    self.outputSelector1.showHidden = False
    self.outputSelector1.showChildNodeTypes = False
    self.outputSelector1.setMRMLScene( slicer.mrmlScene )
    self.outputSelector1.setToolTip( "Pick output segmentation volume." )
    parametersFormLayout.addRow("Output T2-MRI Segmentation: ", self.outputSelector1)

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
    logic = T2ProcessLogic()
    logic.run(self.inputSelector1.currentNode(), self.inputSelector2.currentNode(), self.inputSelector3.currentNode(), self.outputSelector1.currentNode())
#
# T2ProcessLogic
#

class T2ProcessLogic(ScriptedLoadableModuleLogic):
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

  def isValidInputData(self, inputVolumeNode1, inputVolumeNode2, inputModelNode):
    """Validates that inputs are not the same
    """
    if not inputVolumeNode1:
      logging.debug('isValidInputData failed: not all input volume nodes defined')
      return False
    if not inputVolumeNode2:
      logging.debug('isValidInputData failed: not all input volume nodes defined')
      return False
    if not inputModelNode:
      logging.debug('isValidInputData failed: no input model node defined')
      return False
    if inputVolumeNode1.GetID()==inputVolumeNode2.GetID():
      logging.debug('isValidInputData failed: input volume nodes are the same. Select a new volume to avoid this error.')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode1, inputVolumeNode2, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if inputVolumeNode1.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    if inputVolumeNode1.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def run(self, inputT2Volume, inputT2Segment, inputUSModel, outputT2Segment):
    """
    Run the actual algorithm
    """

    # Check that data is valid before proceeding
    if not self.isValidInputData(inputT2Volume, inputT2Segment, inputUSModel):
      slicer.util.errorDisplay('Check that inputs are correctly defined.')
      return False

    if not self.isValidInputOutputData(inputT2Volume, inputT2Segment, outputT2Segment):
      slicer.util.errorDisplay('Check that Inputs and Outputs are defined correctly.')
      return False

    logging.info('Processing started')

    #  make a model of the T2 segmentation for smoothing

    parameters = {} # set parameters
    parameters["InputVolume"] = inputT2Segment.GetID()
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

    numNodes = slicer.mrmlScene.GetNumberOfNodesByClass( "vtkMRMLModelHierarchyNode" )
    outHierarchy = None
    
    if numNodes > 0:
      # user wants to delete any existing models, so take down hierarchy and
      # delete the model nodes
      rr = range(numNodes)
      rr.reverse()
      for n in rr:
        node = slicer.mrmlScene.GetNthNodeByClass( n, "vtkMRMLModelHierarchyNode" )
        slicer.mrmlScene.RemoveNode( node.GetModelNode() )
        slicer.mrmlScene.RemoveNode( node )

    if not outHierarchy:
      outHierarchy = slicer.vtkMRMLModelHierarchyNode()
      outHierarchy.SetScene( slicer.mrmlScene )
      outHierarchy.SetName( "MRI Models" )
      slicer.mrmlScene.AddNode( outHierarchy )

    parameters["ModelSceneFile"] = outHierarchy

    slicer.cli.run(slicer.modules.modelmaker, None, parameters, wait_for_completion=True)

    slicer.cli(modelNode = getNode('Model_1_1'))

    print modelNode


    print outHierarchy

    logging.info('Processing completed')

    return True


class T2ProcessTest(ScriptedLoadableModuleTest):
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
    self.test_T2Process1()

  def test_T2Process1(self):
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
    logic = T2ProcessLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
