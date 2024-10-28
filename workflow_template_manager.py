# -*- coding: utf-8 -*-

#******************************************************************************
#
# Metatools
# ---------------------------------------------------------
# Metadata browser/editor
#
# Copyright (C) 2011 NextGIS (info@nextgis.ru)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/copyleft/gpl.html>. You can also obtain it by writing
# to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.
#
#******************************************************************************

#from PyQt4.QtGui import 
from builtins import str
from builtins import object
from qgis.PyQt.QtCore import QFile
from qgis.PyQt.QtXml import QDomDocument

from past.builtins import str

import os, codecs

class WorkflowTemplateManager(object):
  SUBFOLDER = "templates/workflow"
  EXT = ".xml"

  def __init__(self, basePluginPath):
    self.basePluginPath = str(basePluginPath)

  def getTemplatesPath(self):
    return os.path.join(self.basePluginPath, self.SUBFOLDER)

  def getTemplateFilePath(self, templateName):
    return os.path.join(self.getTemplatesPath(), str(templateName) + self.EXT)

  def getTemplateList(self):
    templatesList = []
    for filename in os.listdir(self.getTemplatesPath()):
      name, ext = os.path.splitext(filename)
      if ext == self.EXT:
        templatesList.append(name)
    return templatesList

  def loadTemplate(self, templateName):
    # TODO: more cheks on struct
    template = WorkflowTemplate()
    templateFile = QFile(self.getTemplateFilePath(templateName))

    xmlTemplate = QDomDocument()
    xmlTemplate.setContent(templateFile)

    root = xmlTemplate.documentElement()
    nameElement = root.elementsByTagName("Name").at(0)
    descriptionElement = root.elementsByTagName("Description").at(0)

    template.name = nameElement.childNodes().at(0).nodeValue()
    template.description = descriptionElement.childNodes().at(0).nodeValue()

    return template

  def saveTemplate(self, template):
    xmlTemplate = QDomDocument()

    # create root
    root = xmlTemplate.createElement("WorkflowTemplate")
    xmlTemplate.appendChild(root)

    # set name
    element = xmlTemplate.createElement("Name")
    textNode = xmlTemplate.createTextNode(template.name)
    element.appendChild(textNode)
    root.appendChild(element)

    # set desc
    element = xmlTemplate.createElement("Description")
    textNode = xmlTemplate.createTextNode(template.description)
    element.appendChild(textNode)
    root.appendChild(element)

    templateFile = codecs.open(self.getTemplateFilePath(template.name), "w", encoding="utf-8")
    templateFile.write(str(xmlTemplate.toString()))
    templateFile.close()

  def removeTemplate(self, templateName):
    os.remove(self.getTemplateFilePath(templateName))

class WorkflowTemplate(object):
  def __init__(self, name = None, description = None):
    self.name = name
    self.description = description

  def stringRepresentation(self):
    return self.name + '::' + self.description
