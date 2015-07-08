import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import time

import SimpleITK as sitk
import sitkUtils

#
# CustomRegister
#

class CustomRegister(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "CustomRegister"
    self.parent.categories = ["Custom"]
    self.parent.dependencies = ['SegmentationSmoothing','QuadEdgeSurfaceMesher']
    self.parent.contributors = ["Andrey Fedorov (BWH), Andras Lasso (Queen's University), Tyler Glass (Nightingale Lab)"]
    self.parent.helpText = """
    This module performs distance-based image registration using segmentations 
    of the structure of interest. The structure should be segmented in both fixed and moving images.
    The actual moving and fixed images are optional, and if available will be 
    used to generate registered image and visualize the results.
    See <a href=http://wiki.slicer.org/slicerWiki/index.php/Documentation/Nightly/Modules/CustomRegister>
    online documentation</a> for details.
    """
    self.parent.acknowledgementText = """
    Development of this module was supported in part by NIH through grants
    R01 CA111288, P41 RR019703 and U24 CA180918.
    """

#
# CustomRegisterWidget
#

class CustomRegisterWidget(ScriptedLoadableModuleWidget):
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
    # fixed image selector
    #
    self.fixedImageSelector = slicer.qMRMLNodeComboBox()
    self.fixedImageSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.fixedImageSelector.selectNodeUponCreation = True
    self.fixedImageSelector.addEnabled = True
    self.fixedImageSelector.removeEnabled = False
    self.fixedImageSelector.noneEnabled = True
    self.fixedImageSelector.showHidden = False
    self.fixedImageSelector.showChildNodeTypes = False
    self.fixedImageSelector.setMRMLScene( slicer.mrmlScene )
    self.fixedImageSelector.setToolTip( "Fixed image (optional)" )
    parametersFormLayout.addRow("Fixed Image: ", self.fixedImageSelector)

    #
    # fixed image label selector
    #
    self.fixedImageLabelSelector = slicer.qMRMLNodeComboBox()
    self.fixedImageLabelSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.fixedImageLabelSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 ) # this one is a labelmap
    self.fixedImageLabelSelector.selectNodeUponCreation = True
    self.fixedImageLabelSelector.addEnabled = False
    self.fixedImageLabelSelector.removeEnabled = False
    self.fixedImageLabelSelector.noneEnabled = False
    self.fixedImageLabelSelector.showHidden = False
    self.fixedImageLabelSelector.showChildNodeTypes = False
    self.fixedImageLabelSelector.setMRMLScene( slicer.mrmlScene )
    self.fixedImageLabelSelector.setToolTip( "Segmentation of the fixed image" )
    parametersFormLayout.addRow("Segmentation of the fixed Image: ", self.fixedImageLabelSelector)

    #
    # fixed image label for similarity
    #
    self.fixedImageSimilarityLabel = slicer.qMRMLNodeComboBox()
    self.fixedImageSimilarityLabel.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.fixedImageSimilarityLabel.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 ) # this one is a labelmap
    self.fixedImageSimilarityLabel.selectNodeUponCreation = True
    self.fixedImageSimilarityLabel.addEnabled = False
    self.fixedImageSimilarityLabel.removeEnabled = False
    self.fixedImageSimilarityLabel.noneEnabled = False
    self.fixedImageSimilarityLabel.showHidden = False
    self.fixedImageSimilarityLabel.showChildNodeTypes = False
    self.fixedImageSimilarityLabel.setMRMLScene( slicer.mrmlScene )
    self.fixedImageSimilarityLabel.setToolTip( "Label to compare using Similarity Metric" )
    parametersFormLayout.addRow("Fixed Image Similarity Label: ", self.fixedImageSimilarityLabel)

    #
    # moving image selector
    #
    self.movingImageSelector = slicer.qMRMLNodeComboBox()
    self.movingImageSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.movingImageSelector.selectNodeUponCreation = True
    self.movingImageSelector.addEnabled = False
    self.movingImageSelector.removeEnabled = False
    self.movingImageSelector.noneEnabled = True
    self.movingImageSelector.showHidden = False
    self.movingImageSelector.showChildNodeTypes = False
    self.movingImageSelector.setMRMLScene( slicer.mrmlScene )
    self.movingImageSelector.setToolTip( "Moving image (optional)" )
    parametersFormLayout.addRow("Moving Image: ", self.movingImageSelector)

    #
    # moving image label selector
    #
    self.movingImageLabelSelector = slicer.qMRMLNodeComboBox()
    self.movingImageLabelSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.movingImageLabelSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 ) # this one is a labelmap
    self.movingImageLabelSelector.selectNodeUponCreation = True
    self.movingImageLabelSelector.addEnabled = False
    self.movingImageLabelSelector.removeEnabled = False
    self.movingImageLabelSelector.noneEnabled = False
    self.movingImageLabelSelector.showHidden = False
    self.movingImageLabelSelector.showChildNodeTypes = False
    self.movingImageLabelSelector.setMRMLScene( slicer.mrmlScene )
    self.movingImageLabelSelector.setToolTip( "Segmentation of the moving image" )
    parametersFormLayout.addRow("Segmentation of the moving Image: ", self.movingImageLabelSelector)

    #
    # moving image label for similarity
    #
    self.movingImageSimilarityLabel = slicer.qMRMLNodeComboBox()
    self.movingImageSimilarityLabel.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.movingImageSimilarityLabel.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 ) # this one is a labelmap
    self.movingImageSimilarityLabel.selectNodeUponCreation = True
    self.movingImageSimilarityLabel.addEnabled = False
    self.movingImageSimilarityLabel.removeEnabled = False
    self.movingImageSimilarityLabel.noneEnabled = False
    self.movingImageSimilarityLabel.showHidden = False
    self.movingImageSimilarityLabel.showChildNodeTypes = False
    self.movingImageSimilarityLabel.setMRMLScene( slicer.mrmlScene )
    self.movingImageSimilarityLabel.setToolTip( "Label to compare using Similarity Metric" )
    parametersFormLayout.addRow("Moving Image Similarity Label: ", self.movingImageSimilarityLabel)

    #
    # Affine output transform selector
    #
    self.affineTransformSelector = slicer.qMRMLNodeComboBox()
    self.affineTransformSelector.nodeTypes = ( ("vtkMRMLTransformNode"), "" )
    self.affineTransformSelector.selectNodeUponCreation = True
    self.affineTransformSelector.addEnabled = True
    self.affineTransformSelector.removeEnabled = False
    self.affineTransformSelector.noneEnabled = False
    self.affineTransformSelector.showHidden = False
    self.affineTransformSelector.showChildNodeTypes = False
    self.affineTransformSelector.baseName = 'Affine Transform'
    self.affineTransformSelector.setMRMLScene( slicer.mrmlScene )
    self.affineTransformSelector.setToolTip( "Registration affine transform" )
    parametersFormLayout.addRow("Registration affine transform: ", self.affineTransformSelector)

    #
    # B-spline output transform selector
    #
    self.bsplineTransformSelector = slicer.qMRMLNodeComboBox()
    self.bsplineTransformSelector.nodeTypes = ( ("vtkMRMLTransformNode"), "" )
    self.bsplineTransformSelector.selectNodeUponCreation = True
    self.bsplineTransformSelector.addEnabled = True
    self.bsplineTransformSelector.removeEnabled = False
    self.bsplineTransformSelector.noneEnabled = False
    self.bsplineTransformSelector.showHidden = False
    self.bsplineTransformSelector.showChildNodeTypes = False
    self.bsplineTransformSelector.baseName = 'Deformable Transform'
    self.bsplineTransformSelector.setMRMLScene( slicer.mrmlScene )
    self.bsplineTransformSelector.setToolTip( "Registration b-spline transform" )
    parametersFormLayout.addRow("Registration B-spline Transform: ", self.bsplineTransformSelector)

    #
    # Display (before or after transform)
    #

    self.registrationModeGroup = qt.QButtonGroup()
    self.noRegistrationRadio = qt.QRadioButton('Before registration')
    self.linearRegistrationRadio = qt.QRadioButton('After linear registration')
    self.deformableRegistrationRadio = qt.QRadioButton('After deformable registration')
    self.noRegistrationRadio.setChecked(1)
    self.registrationModeGroup.addButton(self.noRegistrationRadio,1)
    self.registrationModeGroup.addButton(self.linearRegistrationRadio,2)
    self.registrationModeGroup.addButton(self.deformableRegistrationRadio,3)
    parametersFormLayout.addRow(qt.QLabel("Visualization"))
    parametersFormLayout.addRow("",self.noRegistrationRadio)
    parametersFormLayout.addRow("",self.linearRegistrationRadio)
    parametersFormLayout.addRow("",self.deformableRegistrationRadio)

    self.registrationModeGroup.connect('buttonClicked(int)',self.onVisualizationModeClicked)

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
    #self.onSelect()

    self.parameterNode = slicer.vtkMRMLScriptedModuleNode()

    '''
    TODO:
     * improve GUI structure - separate parameters and visualization
     * improve interaction signal/slots

    '''

  def cleanup(self):
    pass

  def onSelect(self):
    # self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()
    pass

  def onApplyButton(self):
    logic = CustomRegisterLogic()

    self.parameterNode.SetAttribute('FixedImageNodeID',            self.fixedImageSelector.currentNode().GetID())
    self.parameterNode.SetAttribute('FixedLabelNodeID',            self.fixedImageLabelSelector.currentNode().GetID())
    self.parameterNode.SetAttribute('FixedSimilarityLabelNodeID',  self.fixedImageSimilarityLabel.currentNode().GetID())

    self.parameterNode.SetAttribute('MovingImageNodeID',           self.movingImageSelector.currentNode().GetID())
    self.parameterNode.SetAttribute('MovingLabelNodeID',           self.movingImageLabelSelector.currentNode().GetID())
    self.parameterNode.SetAttribute('MovingSimilarityLabelNodeID', self.movingImageSimilarityLabel.currentNode().GetID())

    self.parameterNode.SetAttribute('AffineTransformNodeID',       self.affineTransformSelector.currentNode().GetID())
    self.parameterNode.SetAttribute('BSplineTransformNodeID',      self.bsplineTransformSelector.currentNode().GetID())

    logic.run(self.parameterNode)
    

    # configure the GUI
    #logic.showResults(self.parameterNode)
    #self.noRegistrationRadio.checked = 1
    #self.onVisualizationModeClicked(1)

    return

  def onVisualizationModeClicked(self,mode):

    if self.parameterNode.GetAttribute('MovingImageNodeID'):
      movingVolume = slicer.mrmlScene.GetNodeByID(self.parameterNode.GetAttribute('MovingImageNodeID'))
    else:
      movingVolume = slicer.mrmlScene.GetNodeByID(self.parameterNode.GetAttribute('MovingLabelDistanceMapID'))

    movingSurface = slicer.mrmlScene.GetNodeByID(self.parameterNode.GetAttribute('MovingLabelSurfaceID'))

    affineTransform    = slicer.mrmlScene.GetNodeByID(self.parameterNode.GetAttribute('AffineTransformNodeID'))
    bsplineTransform   = slicer.mrmlScene.GetNodeByID(self.parameterNode.GetAttribute('BSplineTransformNodeID'))
    affineDisplayNode  = affineTransform.GetDisplayNode()
    bsplineDisplayNode = bsplineTransform.GetDisplayNode()

    if mode == 1:
      movingVolume.SetAndObserveTransformNodeID('')
      movingSurface.SetAndObserveTransformNodeID('')
      affineDisplayNode.SetSliceIntersectionVisibility(0)
      bsplineDisplayNode.SetSliceIntersectionVisibility(0)
    if mode == 2:
      movingVolume.SetAndObserveTransformNodeID(affineTransform.GetID())
      movingSurface.SetAndObserveTransformNodeID(affineTransform.GetID())
      affineDisplayNode.SetSliceIntersectionVisibility(1)
      bsplineDisplayNode.SetSliceIntersectionVisibility(0)
      affineDisplayNode.SetVisualizationMode(1)
    if mode == 3:
      movingVolume.SetAndObserveTransformNodeID(bsplineTransform.GetID())
      movingSurface.SetAndObserveTransformNodeID(bsplineTransform.GetID())
      affineDisplayNode.SetSliceIntersectionVisibility(0)
      bsplineDisplayNode.SetSliceIntersectionVisibility(1)
      bsplineDisplayNode.SetVisualizationMode(1)
    return

#
# CustomRegisterLogic
#

class CustomRegisterLogic(ScriptedLoadableModuleLogic):
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

  def run(self, parameterNode):
    """
    Run the actual algorithm
    """
    
    fixedLabelNodeID      = parameterNode.GetAttribute('FixedLabelNodeID')
    movingLabelNodeID     = parameterNode.GetAttribute('MovingLabelNodeID')

    fixedSimilarityLabelNodeID      = parameterNode.GetAttribute('FixedSimilarityLabelNodeID')
    movingSimilarityLabelNodeID     = parameterNode.GetAttribute('MovingSimilarityLabelNodeID')
    fixedSimilarityLabelNode        = slicer.util.getNode( fixedSimilarityLabelNodeID)
    movingSimilarityLabelNode       = slicer.util.getNode(movingSimilarityLabelNodeID)
    
    affineTransformNode   = slicer.mrmlScene.GetNodeByID(parameterNode.GetAttribute('AffineTransformNodeID'))
    bsplineTransformNode  = slicer.mrmlScene.GetNodeByID(parameterNode.GetAttribute('BSplineTransformNodeID'))

    # Print to Slicer CLI
    logging.info('Processing started')
    start_time_overall = time.time() # start timer

    # crop the labels
    (bbMin,bbMax) = self.getBoundingBox(fixedLabelNodeID, movingLabelNodeID)

    print("Before preprocessing")

    fixedLabelDistanceMap = self.preProcessLabel(fixedLabelNodeID, bbMin, bbMax)
    parameterNode.SetAttribute('FixedLabelDistanceMapID',fixedLabelDistanceMap.GetID())
    fixedLabelSmoothed = slicer.util.getNode(slicer.mrmlScene.GetNodeByID(fixedLabelNodeID).GetName()+'-Smoothed')
    parameterNode.SetAttribute('FixedLabelSmoothedID',fixedLabelSmoothed.GetID())
    print('Fixed label processing done')

    movingLabelDistanceMap = self.preProcessLabel(movingLabelNodeID, bbMin, bbMax)
    parameterNode.SetAttribute('MovingLabelDistanceMapID',movingLabelDistanceMap.GetID())
    movingLabelSmoothed = slicer.util.getNode(slicer.mrmlScene.GetNodeByID(movingLabelNodeID).GetName()+'-Smoothed')
    parameterNode.SetAttribute('MovingLabelSmoothedID',movingLabelSmoothed.GetID())
    print('Moving label processing done')

    # run affine registration
    registrationParameters = {'fixedVolume':fixedLabelDistanceMap.GetID(), 'movingVolume':movingLabelDistanceMap.GetID(),'useRigid':True,'useAffine':True,'numberOfSamples':'10000','costMetric':'MSE','outputTransform':affineTransformNode.GetID()}
    slicer.cli.run(slicer.modules.brainsfit, None, registrationParameters, wait_for_completion=True)
    parameterNode.SetAttribute('AffineTransformNodeID',affineTransformNode.GetID())
    print('affineRegistrationCompleted!')

    # run bspline registration (comment out for experiment)
    # registrationParameters = {'fixedVolume':fixedLabelDistanceMap.GetID(), 'movingVolume':movingLabelDistanceMap.GetID(),'useBSpline':True,'splineGridSize':'3,3,3','numberOfSamples':'10000','costMetric':'MSE','bsplineTransform':bsplineTransformNode.GetID(),'initialTransform':affineTransformNode.GetID()}
    # slicer.cli.run(slicer.modules.brainsfit, None, registrationParameters, wait_for_completion=True)
    # parameterNode.SetAttribute('BSplineTransformNodeID',bsplineTransformNode.GetID())
    # print('bsplineRegistrationCompleted!')

    # Initialize Results CSV file
    #results = []
    #results.append([0,0,self.ComputeSimilarityMetric(fixedSimilarityLabelNode,movingSimilarityLabelNode)]) # compute similarity metric b/w fixed and moving similarity
    #print results

    numSamples = [100,1000,10000,50000,100000] 

    # Smooth fixed label prior to looping over registration
    self.LabelMapSmoothing(fixedSimilarityLabelNode, fixedSimilarityLabelNode, 0.4)

    # Initialize Inputs
    RegisterTimes = []
    SimilarityValues = []

    for numSamp in numSamples:
        newTransformNode = self.CreateNewTransform()
        register_time, DeformableTransformNode = self.bsplineRegisterNumSamp(fixedLabelDistanceMap,movingLabelDistanceMap,newTransformNode,affineTransformNode,numSamp)
        newVolumeNode = self.CreateNewVolume() # create a new node to transform and compute similarity metric
        self.LabelMapSmoothing(movingSimilarityLabelNode, newVolumeNode, 0.4)
        self.transformNodewithBspline(newVolumeNode, DeformableTransformNode)
        self.processTransformedNode(newVolumeNode)
        similarityValue = self.ComputeSimilarityMetric(fixedSimilarityLabelNode, newVolumeNode)

        # Append values to variables
        RegisterTimes.append(register_time)
        SimilarityValues.append(similarityValue)

    # Print variables to Slicer CLI
    # print results
    print "Number of Samples",
    print numSamples
    print "Reg. Times",
    print RegisterTimes
    print "Similarity Values",
    print SimilarityValues

    # Print results to Slicer CLI
    end_time_overall = time.time()
    logging.info('Processing completed')
    print('Overall Algorithm Time: % 0.1f seconds') % float(end_time_overall-start_time_overall)

    return True

  def CreateNewTransform(self):
    transformNode = slicer.vtkMRMLTransformNode()
    slicer.mrmlScene.AddNode(transformNode)
    transformNode.CreateDefaultStorageNode()

    return transformNode

  def CreateNewVolume(self):
    imageSize=[64, 64, 64]
    imageSpacing=[1.0, 1.0, 1.0]
    voxelType=vtk.VTK_UNSIGNED_CHAR
    # Create an empty image volume
    imageData=vtk.vtkImageData()
    imageData.SetDimensions(imageSize)
    imageData.AllocateScalars(voxelType, 1)
    thresholder=vtk.vtkImageThreshold()
    thresholder.SetInputData(imageData)
    thresholder.SetInValue(0)
    thresholder.SetOutValue(0)
    # Create volume node
    volumeNode=slicer.vtkMRMLScalarVolumeNode()
    volumeNode.SetSpacing(imageSpacing)
    volumeNode.SetImageDataConnection(thresholder.GetOutputPort())
    # Add volume to scene
    slicer.mrmlScene.AddNode(volumeNode)
    displayNode=slicer.vtkMRMLScalarVolumeDisplayNode()
    slicer.mrmlScene.AddNode(displayNode)
    colorNode = slicer.util.getNode('Grey')
    displayNode.SetAndObserveColorNodeID(colorNode.GetID())
    volumeNode.SetAndObserveDisplayNodeID(displayNode.GetID())
    volumeNode.CreateDefaultStorageNode()

    return volumeNode

  def bsplineRegisterNumSamp(self,fixedLabelDistanceMap,movingLabelDistanceMap,newTransformNode,affineTransformNode,numSamp):
    """ Performs bspline registration for inputted nodes with inputted number of samples
    """
    # Print to Slicer CLI
    print('Running BSpline Registration...'),
    start_time = time.time()

    registrationParameters = {'fixedVolume':fixedLabelDistanceMap.GetID(), 'movingVolume':movingLabelDistanceMap.GetID(),'useBSpline':True,'splineGridSize':'3,3,3','numberOfSamples':str(numSamp),'costMetric':'MSE','bsplineTransform':newTransformNode.GetID(),'initialTransform':affineTransformNode.GetID()}
    slicer.cli.run(slicer.modules.brainsfit, None, registrationParameters, wait_for_completion=True)
    print('bsplineRegistrationCompleted!'),

    # print to Slicer CLI
    end_time = time.time()
    print(('(%0.2f s)')) % float(end_time-start_time)

    return float(end_time-start_time), newTransformNode

  def transformNodewithBspline(self, movingSimilarityLabel, bsplineTransform):
    # tranform input node using bspline transform from registration
    movingSimilarityLabel.SetAndObserveTransformNodeID(bsplineTransform.GetID())
    slicer.vtkSlicerTransformLogic().hardenTransform(movingSimilarityLabel) # hardens transform

  def processTransformedNode(self, inputNode):
    # threshold and smooth an input node
    self.ThresholdScalarVolume(inputNode, 20) # set to label value of 20
    self.LabelMapSmoothing(inputNode, inputNode, 0.3)

  def ComputeSimilarityMetric(self, volumeA, volumeB):
    # Computes the similarity metric for the labels chosen by thew widget
    import SimpleITK as sitk
    import sitkUtils

    A_img  = sitk.ReadImage(sitkUtils.GetSlicerITKReadWriteAddress( volumeA.GetName()))
    B_img = sitk.ReadImage(sitkUtils.GetSlicerITKReadWriteAddress(  volumeB.GetName()))
    similarity_filter = sitk.SimilarityIndexImageFilter()
    similarity_filter.Execute(A_img, B_img)

    return similarity_filter.GetSimilarityIndex()

  def LabelMapSmoothing(self, inputVolume, outputVolume, Sigma, *labelNumber):
    """ Smooths an input volume labelmap using value of sigma provided (number from 0-5). Optionally smooths only selected labels if more arguments passed
    """
    # Print to Slicer CLI
    print('Additional Label Map Smoothing...'),
    start_time = time.time()

    # Run the slicer module in CLI
    cliParams = {'inputVolume': inputVolume.GetID(), 'outputVolume': outputVolume.GetID(), 'gaussianSigma': Sigma} # input and output defined as same
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

  def showResults(self,parameterNode):
    # duplicate moving volume

    self.makeSurfaceModels(parameterNode)

    print('Surface name:'+parameterNode.GetAttribute('MovingLabelSurfaceID'))

    volumesLogic = slicer.modules.volumes.logic()
    movingImageID = parameterNode.GetAttribute('MovingImageNodeID')
    if not movingImageID:
      movingImageID = parameterNode.GetAttribute('MovingLabelDistanceMapID')

    fixedImageID = parameterNode.GetAttribute('FixedImageNodeID')
    if not fixedImageID:
      fixedImageID = parameterNode.GetAttribute('FixedLabelDistanceMapID')

    movingImageNode = slicer.mrmlScene.GetNodeByID(movingImageID)

    # display intersection of the fixed label surface in all slices
    fixedLabelSurface = slicer.mrmlScene.GetNodeByID(parameterNode.GetAttribute('FixedLabelSurfaceID'))
    modelDisplayNode = fixedLabelSurface.GetDisplayNode()
    print('Set slice intersection')
    modelDisplayNode.SetSliceIntersectionVisibility(1)
    modelDisplayNode.SetSliceIntersectionThickness(3)

    movingImageCloneID = parameterNode.GetAttribute('MovingImageCloneID')
    if movingImageCloneID:
      slicer.mrmlScene.RemoveNode(slicer.mrmlScene.GetNodeByID(movingImageCloneID))
    
    movingImageClone = volumesLogic.CloneVolume(movingImageNode,'MovingImageCopy')
    parameterNode.SetAttribute('MovingImageCloneID',movingImageClone.GetID())

    lm = slicer.app.layoutManager()
    lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)

    sliceCompositeNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLSliceCompositeNode')
    sliceCompositeNodes.SetReferenceCount(sliceCompositeNodes.GetReferenceCount()-1)

    for i in range(sliceCompositeNodes.GetNumberOfItems()):
      scn = sliceCompositeNodes.GetItemAsObject(i)
      scn.SetForegroundVolumeID(fixedImageID)
      scn.SetBackgroundVolumeID(movingImageID)
      scn.SetLabelVolumeID('')

    # TODO: call the code to configure views based on the mode selected
    
    return

    # create surface model for the moving volume segmentation
    # apply transforms based on user input (none, affine, deformable)
    # (need to create another panel in the GUI for visualization)
    # enable transform visualization in-slice and 3d

  def makeSurfaceModels(self,parameterNode):
    fixedLabel  = slicer.util.getNode(parameterNode.GetAttribute('FixedLabelNodeID'))
    movingLabel = slicer.util.getNode(parameterNode.GetAttribute('MovingLabelNodeID'))

    # Create surface model for fixed label
    fixedModel = slicer.vtkMRMLModelNode()
    slicer.mrmlScene.AddNode(fixedModel)
    fixedModel.SetName(fixedLabel.GetName()+'-surface')
    parameterNode.SetAttribute('FixedLabelSurfaceID',fixedModel.GetID())
    print('Created a new model: '+fixedModel.GetID()+' '+fixedModel.GetName())

    parameters = {'inputImageName':parameterNode.GetAttribute('FixedLabelSmoothedID'),'outputMeshName':fixedModel.GetID()}
    slicer.cli.run(slicer.modules.quadedgesurfacemesher,None,parameters,wait_for_completion=True)
    fixedModel.GetDisplayNode().SetColor(0.9,0.9,0)

    # Create surface model for moving label
    movingModel = slicer.vtkMRMLModelNode()
    slicer.mrmlScene.AddNode(movingModel)
    movingModel.SetName(movingLabel.GetName()+'-surface')
    parameterNode.SetAttribute('MovingLabelSurfaceID',movingModel.GetID())
    print('Created a new model: '+movingModel.GetID()+' '+movingModel.GetName())

    parameters = {'inputImageName':parameterNode.GetAttribute('MovingLabelSmoothedID'),'outputMeshName':movingModel.GetID()}
    slicer.cli.run(slicer.modules.quadedgesurfacemesher,None,parameters,wait_for_completion=True)
    movingModel.GetDisplayNode().SetColor(0,0.7,0.9)

    return

  def getBoundingBox(self,fixedLabelNodeID,movingLabelNodeID):

    ls = sitk.LabelStatisticsImageFilter()

    fixedLabelNode = slicer.mrmlScene.GetNodeByID(fixedLabelNodeID)
    movingLabelNode = slicer.mrmlScene.GetNodeByID(movingLabelNodeID)

    fixedLabelAddress = sitkUtils.GetSlicerITKReadWriteAddress(fixedLabelNode.GetName())
    movingLabelAddress = sitkUtils.GetSlicerITKReadWriteAddress(movingLabelNode.GetName())

    fixedLabelImage = sitk.ReadImage(fixedLabelAddress)
    movingLabelImage = sitk.ReadImage(movingLabelAddress)

    cast = sitk.CastImageFilter()
    cast.SetOutputPixelType(2)
    unionLabelImage = (cast.Execute(fixedLabelImage) + cast.Execute(movingLabelImage)) > 0
    unionLabelImage = cast.Execute(unionLabelImage)

    ls.Execute(unionLabelImage,unionLabelImage)
    bb = ls.GetBoundingBox(1)
    print(str(bb))

    size = unionLabelImage.GetSize()
    bbMin = (max(0,bb[0]-30),max(0,bb[2]-30),max(0,bb[4]-5))
    bbMax = (size[0]-min(size[0],bb[1]+30),size[1]-min(size[1],bb[3]+30),size[2]-(min(size[2],bb[5]+5)))

    return (bbMin,bbMax)

  def preProcessLabel(self,labelNodeID,bbMin,bbMax):

    # Start the timer
    start_time = time.time()

    print('Label node ID: '+labelNodeID)

    labelNode = slicer.util.getNode(labelNodeID)

    labelNodeAddress = sitkUtils.GetSlicerITKReadWriteAddress(labelNode.GetName())

    print('Label node address: '+str(labelNodeAddress))

    labelImage = sitk.ReadImage(labelNodeAddress)

    print('Read image: '+str(labelImage))

    crop = sitk.CropImageFilter()
    crop.SetLowerBoundaryCropSize(bbMin)
    crop.SetUpperBoundaryCropSize(bbMax)
    croppedImage = crop.Execute(labelImage)

    print('Cropped image done: '+str(croppedImage))

    croppedLabelName = labelNode.GetName()+'-Cropped'
    sitkUtils.PushToSlicer(croppedImage,croppedLabelName,overwrite=True)
    print('Cropped volume pushed')

    croppedLabel = slicer.util.getNode(croppedLabelName)

    print('Smoothed image done')

    smoothLabelName = labelNode.GetName()+'-Smoothed'
    smoothLabel = self.createVolumeNode(smoothLabelName)

    # smooth the labels
    smoothingParameters = {'inputImageName':croppedLabel.GetID(), 'outputImageName':smoothLabel.GetID()}
    print(str(smoothingParameters))
    cliNode = slicer.cli.run(slicer.modules.segmentationsmoothing, None, smoothingParameters, wait_for_completion = True)

    # crop the bounding box
    
    '''
    TODO:
     * output volume node probably not needed here
     * intermediate nodes should probably be hidden - AGREED!
    '''

    dt = sitk.SignedMaurerDistanceMapImageFilter()
    dt.SetSquaredDistance(False)
    distanceMapName = labelNode.GetName()+'-DistanceMap'
    print('Reading smoothed image: '+smoothLabel.GetID())
    smoothLabelAddress = sitkUtils.GetSlicerITKReadWriteAddress(smoothLabel.GetName())    
    smoothLabelImage = sitk.ReadImage(smoothLabelAddress)
    print(smoothLabelAddress)
    distanceImage = dt.Execute(smoothLabelImage)
    sitkUtils.PushToSlicer(distanceImage, distanceMapName, overwrite=True)

    # print to Slicer CLI
    end_time = time.time()
    print('Label preprocessing done (%0.2f s)') % float(end_time-start_time)

    return slicer.util.getNode(distanceMapName)

  def createVolumeNode(self,name):
    import sitkUtils
    node = sitkUtils.CreateNewVolumeNode(name,overwrite=True)
    storageNode = slicer.vtkMRMLNRRDStorageNode()
    slicer.mrmlScene.AddNode(storageNode)
    node.SetAndObserveStorageNodeID(storageNode.GetID())
    return node

class CustomRegisterTest(ScriptedLoadableModuleTest):
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
    self.test_CustomRegister1()

  def test_CustomRegister1(self):
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
    logic = CustomRegisterLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')


    '''

    TODO:
     * add main() so that registration could be run from command line

    '''
