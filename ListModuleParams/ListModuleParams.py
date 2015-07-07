import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

### Choose Module to list parameters for
module_name = slicer.modules.transforms


### Processing Code
class ListModuleParams(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "ListModuleParams" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Custom"]
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

    cliModule = module_name ### SELECT EXTENSION HERE!
    n=cliModule.cliModuleLogic().CreateNode()
    print '\n'
    print 'Parameter Set for {}:\n'.format(cliModule.name)
    for groupIndex in xrange(0,n.GetNumberOfParameterGroups()):
      for parameterIndex in xrange(0,n.GetNumberOfParametersInGroup(groupIndex)):
        print 'Parameter ({0}/{1}): {2} ({3}) [Default: {4}] [Type: {5}]'.format(groupIndex, parameterIndex, n.GetParameterName(groupIndex, parameterIndex), n.GetParameterLabel(groupIndex, parameterIndex), n.GetParameterDefault(groupIndex, parameterIndex),n.GetParameterType(groupIndex, parameterIndex))
