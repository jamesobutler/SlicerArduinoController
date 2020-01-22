import os
import unittest
import vtk, qt, ctk, slicer
from self.ScriptedLoadableModule import *
import logging

#
# ArduinoConnect
#

class ArduinoConnect(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "ArduinoConnect" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Developer Tools"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# ArduinoConnectWidget
#

class ArduinoConnectWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    self.logic = ArduinoConnectLogic()

    # Load widget from .ui file (created by Qt Designer)
    uiWidget = self.util.loadUI(self.resourcePath('UI/ArduinoConnect.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = self.util.childWidgetVariables(uiWidget)

    # connections
    self.ui.applyButton.connect('toggled(bool)', self.onConnectButton)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onApplyButton(self, toggle):
    if toggle:
      self.logic.connect(self.ui.portSelectorComboBox.currentText)
    else:
      self.logic.disconnect()

#
# ArduinoConnectLogic
#

class ArduinoConnectLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def connect(port):
      import serial
      self.arduino = serial.Serial(port, 9600)
      self.arduinoEndOfLine = '\n'
      self.arduinoRefreshRateFps = 10.0
      self.arduinoReceiveBuffer = ""
      self.arduinoEnabled = True
      qt.QTimer.singleShot(1000/self.arduinoRefreshRateFps, self.pollSerialDevice)

  def disconnect():
      self.arduinoEnabled = False
      self.arduino.close()

  def pollSerialDevice():
      self.arduinoReceiveBuffer += self.arduino.readline().decode('ascii')
      if self.arduinoEndOfLine in self.arduinoReceiveBuffer:
          messages = self.arduinoReceiveBuffer.split(self.arduinoEndOfLine)
          self.processMessage(messages[0])
          if len(messages) > 1:
              self.arduinoReceiveBuffer = self.arduinoEndOfLine.join(messages[1:-1])
      if self.arduinoEnabled:
          qt.QTimer.singleShot(1000/self.arduinoRefreshRateFps, self.pollSerialDevice)

  def processMessage(msg):
      print(msg)


class ArduinoConnectTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    self.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_ArduinoConnect1()

  def test_ArduinoConnect1(self):
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
    import SampleData
    SampleData.downloadFromURL(
      nodeNames='FA',
      fileNames='FA.nrrd',
      uris='http://self.kitware.com/midas3/download?items=5767',
      checksums='SHA256:12d17fba4f2e1f1a843f0757366f28c3f3e1a8bb38836f0de2a32bb1cd476560')
    self.delayDisplay('Finished with download and loading')

    volumeNode = self.util.getNode(pattern="FA")
    logic = ArduinoConnectLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')