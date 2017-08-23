import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import time # for measuring time of processing steps

#
# LoadUltrasound
#
# This module is used to laod and view ARFI U/S for a selected patient number chosen by user.
#

class LoadUltrasound(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Load Ultrasound Dataset"
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
# LoadUltrasoundWidget
#

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

class LoadUltrasoundWidget(ScriptedLoadableModuleWidget):
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

    patientNumberMethodFrame = qt.QFrame(self.parent)
    parametersFormLayout.addRow(patientNumberMethodFrame)
    patientNumberMethodFormLayout = qt.QFormLayout(patientNumberMethodFrame)

    dataFrame = qt.QFrame(self.parent)
    dataFrameLayout = qt.QHBoxLayout()
    dataFrame.setLayout(dataFrameLayout)
    dataLabel = qt.QLabel('Data Directory:', dataFrame)
    dataLabel.setToolTip('Data directory containing "Patient##"')
    dataFrameLayout.addWidget(dataLabel)
    self.DataDirectoryButton = ctk.ctkDirectoryButton(self.parent)
    dataFrameLayout.addWidget(self.DataDirectoryButton)
    patientNumberMethodFormLayout.addRow(dataFrame)

    patientNumberIterationsFrame, self.PatientNumberIterationsSpinBox = \
        numericInputFrame(self.parent, "Patient Number:" , "Tooltip", 59, 110,
                          1, 0)
    patientNumberMethodFormLayout.addRow(patientNumberIterationsFrame)

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
    logic = LoadUltrasoundLogic()
    logic.run(str(int(self.PatientNumberIterationsSpinBox.value)),
              self.DataDirectoryButton.directory)
#
# LoadUltrasoundLogic
#

class LoadUltrasoundLogic(ScriptedLoadableModuleLogic):
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

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def CenterVolume(self, *inputVolumes):
    """ Centers an inputted volume using the image spacing, size, and origin of the volume
    """
    for inputVolume in inputVolumes: # cycle through all input volumes

        # Use image size and spacing to find origin coordinates
        extent = [x-1 for x in inputVolume.GetImageData().GetDimensions()] # subtract 1 from dimensions to get extent
        spacing = [x for x in inputVolume.GetSpacing()]
        new_origin = [a*b/2 for a,b in zip(extent,spacing)]
        new_origin[2] = -new_origin[2] # need to make this value negative to center the volume

        # Set input volume origin to the new origin
        inputVolume.SetOrigin(new_origin)

  def run(self, patientNumber, dataDirectory):
    """
    Run the actual algorithm
    """

    print("\n\n\n\n\n\n\n")
    print( "====================================")
    print("Loading Patient %s" % patientNumber)
    print("From Directory %s" % dataDirectory)

    inputDir = os.path.join(dataDirectory,
                            'Patient' + patientNumber,
                            'Ultrasound')
    slicer.util.loadVolume(os.path.join(inputDir, 'ARFI_Norm_HistEq.nii.gz'))
    ARFI_vol  = slicer.util.getNode('ARFI_Norm_HistEq')
    slicer.util.loadVolume(os.path.join(inputDir, 'Bmode.nii.gz'))
    Bmode_vol = slicer.util.getNode('Bmode')

    # self.CenterVolume(ARFI_vol, Bmode_vol)

    # Load JSON for lesions and print to CLI
    print("\nLesion Data for Patient %s:" % patientNumber)
    import json
    from pprint import pprint

    # from remote_pdb import set_trace; set_trace()

    with open(os.path.join(inputDir, 'ARFI_Lesions.json'), 'r') as json_data:
      d = json.load(json_data)
      json_data.close()
      pprint(d)

    print("====================================")

    return True


class LoadUltrasoundTest(ScriptedLoadableModuleTest):
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
    self.test_LoadUltrasound1()

  def test_LoadUltrasound1(self):
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
    logic = LoadUltrasoundLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
