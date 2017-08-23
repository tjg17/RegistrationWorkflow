import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

# 
# ListModuleParams
# 
# This module is a development tool used to list the paramaters for existing slicerCLI modules
# Change line 89 to choose slicerCLI module that you wish to know parameters for


### Processing Code
class ListModuleParams(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "ListModuleParams" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Prostate"]
    self.parent.dependencies = []
    self.parent.contributors = ["Tyler Glass (Nightingale Lab)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It prints all parameters for a selected module to the Slicer Python Interactor
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# ListModuleParamsWidget
#

class ListModuleParamsWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Module Selection Button
    #
    dummyCollapsibleButton = ctk.ctkCollapsibleButton()
    dummyCollapsibleButton.text = "Select Module (must be CLI)"
    self.layout.addWidget(dummyCollapsibleButton)
    dummyFormLayout = qt.QFormLayout(dummyCollapsibleButton)
    label = qt.QLabel('Module Name:')
    label.setToolTip( "Module Name must be one word w/ 1st letters capitalized (e.g. 'Label Map Smoothing' module becomes 'LabelMapSmoothing'). Module parameters are then listed in the Python terminal (Ctrl+3) " )
    self.__veLabel = qt.QLineEdit()
    dummyFormLayout.addRow(label, self.__veLabel)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = True
    dummyFormLayout.addRow(self.applyButton)
    self.applyButton.connect('clicked(bool)', self.onApplyButton)

  def onApplyButton(self):
    logic = ListModuleParamsLogic()
    logic.run(self.__veLabel.text)


class ListModuleParamsLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def run(self,cliModuleName):
    """ Prints parameters of selected module to python terminal in Slicer"""

    cliModule = slicer.util.getModule(cliModuleName)
    n=cliModule.cliModuleLogic().CreateNode()

    print '\n'
    print 'Parameter Set for {}:\n'.format(cliModule.name)
    for groupIndex in xrange(0,n.GetNumberOfParameterGroups()):
      for parameterIndex in xrange(0,n.GetNumberOfParametersInGroup(groupIndex)):
        print 'Parameter ({0}/{1}): {2} ({3}) [Default: {4}] [Type: {5}]'.format(groupIndex, parameterIndex, n.GetParameterName(groupIndex, parameterIndex), n.GetParameterLabel(groupIndex, parameterIndex), n.GetParameterDefault(groupIndex, parameterIndex),n.GetParameterType(groupIndex, parameterIndex))
