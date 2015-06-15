import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import time # for measuring time of processing steps

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
    self.USinputSelector1.setToolTip( "Select ARFI volume." )
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
    self.USinputSelector2.setToolTip( "Select Bmode volume." )
    parametersFormLayout.addRow("Input Bmode Volume: ", self.USinputSelector2)

    #
    # input ultrasound capsule VTK model
    #
    self.USinputSelector3 = slicer.qMRMLNodeComboBox()
    self.USinputSelector3.nodeTypes = ( ("vtkMRMLModelNode"), "" )
    self.USinputSelector3.selectNodeUponCreation = True
    self.USinputSelector3.addEnabled = False
    self.USinputSelector3.removeEnabled = False
    self.USinputSelector3.noneEnabled = False
    self.USinputSelector3.showHidden = False
    self.USinputSelector3.showChildNodeTypes = False
    self.USinputSelector3.setMRMLScene( slicer.mrmlScene )
    self.USinputSelector3.setToolTip( "Select Ultrasound Capsule Model." )
    parametersFormLayout.addRow("Input U/S Capsule Model: ", self.USinputSelector3)

    #
    # output segmentation selector
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
    self.USoutputSelector1.setToolTip( "Select output capsule segmentation volume." )
    parametersFormLayout.addRow("Output U/S Capsule Segmentation: ", self.USoutputSelector1)

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
    self.MRinputSelector1.setToolTip( "Select axial T2-MRI." )
    parametersFormLayout.addRow("Input T2-MRI Volume: ", self.MRinputSelector1)

    #
    # input T2-MRI segmentation
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
    self.MRinputSelector2.setToolTip( "Select axial T2-MRI segmentation." )
    parametersFormLayout.addRow("Input T2-MRI Capsule Segmentation: ", self.MRinputSelector2)


    #
    # output segmentation selector
    #
    self.MRoutputSelector1 = slicer.qMRMLNodeComboBox()
    self.MRoutputSelector1.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.MRoutputSelector1.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 ) # this one is a labelmap
    self.MRoutputSelector1.selectNodeUponCreation = True
    self.MRoutputSelector1.addEnabled = True
    self.MRoutputSelector1.removeEnabled = True
    self.MRoutputSelector1.renameEnabled = False
    self.MRoutputSelector1.baseName = "mr_cap-label"
    self.MRoutputSelector1.noneEnabled = False
    self.MRoutputSelector1.showHidden = False
    self.MRoutputSelector1.showChildNodeTypes = False
    self.MRoutputSelector1.setMRMLScene( slicer.mrmlScene )
    self.MRoutputSelector1.setToolTip( "Pick output segmentation volume." )
    parametersFormLayout.addRow("Output T2-MRI Capsule Segmentation: ", self.MRoutputSelector1)

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
    logic.run(self.USinputSelector1.currentNode(), self.USinputSelector2.currentNode(), self.USinputSelector3.currentNode(), self.USoutputSelector1.currentNode(), 
              self.MRinputSelector1.currentNode(), self.MRinputSelector2.currentNode(), self.MRoutputSelector1.currentNode())

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

  def CenterVolume(self, inputVolume):
    """ Centers an inputted volume using the image spacing, size, and origin of the volume
    """
    # Print to Slicer CLI
    print('Centering volume...'),
    start_time = time.time()

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

  def US_transform(self, inputARFI_node, inputBmode_node, inputUSModel_node):
    """ Performs inversion transform with [1 1 -1 1] diagonal entries on Ultrasound inputs
    """
    # Print to Slicer CLI
    print('Transforming Ultrasound inputs...'),
    start_time = time.time()

    # Create inverting transform matrix
    invert_transform = vtk.vtkMatrix4x4()
    invert_transform.SetElement(2,2,-1) # put a -1 in 3rd entry of diagonal of matrix

    # Apply transform to input nodes
    inputARFI_node.ApplyTransformMatrix(invert_transform)
    inputBmode_node.ApplyTransformMatrix(invert_transform)
    inputUSModel_node.ApplyTransformMatrix(invert_transform)

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def ModelToLabelMap(self, inputVolume, inputModel, outputVolume):
    """ Converts model into a labelmap on the input volume using 0.1 sample distance so that smaller than Ultrasound voxel size
    """
    # Print to Slicer CLI
    print('Converting Model to Label Map...'),
    start_time = time.time()

    # Run the slicer module in CLI
    cliParams = {'InputVolume': inputVolume.GetID(), 'surface': inputModel.GetID(), 'OutputVolume': outputVolume.GetID(), 'sampleDistance': 0.1, 'labelValue': 10}
    cliNode = slicer.cli.run(slicer.modules.modeltolabelmap, None, cliParams, wait_for_completion=True)
    
    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def MRModelMaker(self, inputMRlabel):
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
    outputMRModel = slicer.util.getNode('Model_1_1')

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

    return outputMRModel    

  def MR_translate(self, movingVolume, movingModel, movingLabel, fixedModel):
    """ Translates MRI capsule and T2 imaging volume to roughly align with US capsule model so T2 prostate is within ARFI image
    """
    # Print to Slicer CLI
    print('Translating T2 volume and MRI model...'),
    start_time = time.time()

    # Find out coordinates of models to be used for translation matrix
    moving_bounds = movingModel.GetPolyData().GetBounds()
    fixed_bounds  =  fixedModel.GetPolyData().GetBounds()

    
    # Define transform matrix
    translate_transform = vtk.vtkMatrix4x4()
    translate_transform.SetElement(2,3,fixed_bounds[5] - moving_bounds[5]) # lines up base of prostate at same value
    translate_transform.SetElement(1,3,fixed_bounds[2] - moving_bounds[2]) # lines up posterior of prostate at same value
    translate_transform.SetElement(0,3,fixed_bounds[0] - moving_bounds[0]) # lines up right side of prostate at same value
    
    # OPTIONAL: print transform to Python
    # print translate_transform 

    # Apply transform to MRI-T2 volume and model
    movingVolume.ApplyTransformMatrix(translate_transform)
    movingModel.ApplyTransformMatrix(translate_transform)
    movingLabel.ApplyTransformMatrix(translate_transform)

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def ResampleVolume(self, inputVolume, referenceVolume):
    """ Resamples and input volume to match reference volume spacing, size, orientation, and origin
    """
    # Print to Slicer CLI
    print('Resampling T2 volume to match ARFI...'),
    start_time = time.time()

    # Run Resample ScalarVectorDWIVolume Module from CLI
    cliParams = {'inputVolume': inputVolume.GetID(), 'outputVolume': inputVolume.GetID(), 'referenceVolume': referenceVolume.GetID()}
    cliNode = slicer.cli.run(slicer.modules.resamplescalarvectordwivolume, None, cliParams, wait_for_completion=True)

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def run(self, inputARFI, inputBmode, inputUSCaps_Model, outputUSCaps_Seg, inputT2, inputMRCaps_Seg, outputMRCaps_Seg):
    """
    Run the actual algorithm
    """

    # Print to Slicer CLI
    logging.info('\n\nProcessing started')
    print('Expected Run Time: 90 seconds') # based on previous trials of the algorithm
    start_time_overall = time.time() # start timer

    # Center the Ultrasound inputs (ultrasound capsule was segmented and modeled on centered volume)
    self.CenterVolume(inputARFI)
    self.CenterVolume(inputBmode)

    # Transform US inputs using inversion transform
    self.US_transform(inputARFI, inputBmode, inputUSCaps_Model)
    
    # Convert US Capsule model to labelmap
    print('Ultrasound: '), 
    self.ModelToLabelMap(inputARFI, inputUSCaps_Model, outputUSCaps_Seg)

    # Make Model of MRI input capsule segmentation using Model Maker Module and define to variable
    intermediateMRCaps_Model = self.MRModelMaker(inputMRCaps_Seg)

    # Transform MRI model and T2 volume to match Ultrasound
    self.MR_translate(inputT2, intermediateMRCaps_Model, inputMRCaps_Seg, inputUSCaps_Model)

    # Resample MRI T2 volume to match volume spacing, size, orientation, and origin of Ultrasound volumes
    self.ResampleVolume(inputT2, inputARFI)

    # Convert MR Capsule model to labelmap with same parameters as resampled T2
    print('MRI: '),
    self.ModelToLabelMap(inputT2, intermediateMRCaps_Model, outputMRCaps_Seg)

    # Print Completion Status to Slicer CLI
    end_time_overall = time.time()
    logging.info('Processing completed')
    print('Overall Run Time: % 0.1f seconds') % float(end_time_overall-start_time_overall)

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
