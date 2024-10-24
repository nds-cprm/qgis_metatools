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

from PyQt4 import uic
#from PyQt4.QtCore import 
from PyQt4.QtGui import QDialog,QDialogButtonBox,QMessageBox
#from PyQt4.QtXml import 
#from PyQt4.QtXmlPatterns import

#from qgis.core import 
#from qgis.gui import

from past.builtins import unicode

import os, sys

from workflow_template_manager import WorkflowTemplateManager, WorkflowTemplate

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/workflow_editor.ui'))

currentPath = os.path.abspath(os.path.dirname(__file__))

class WorkflowEditorDialog(QDialog, FORM_CLASS):
  def __init__(self, parent=None):
    super(WorkflowEditorDialog, self).__init__(parent)
    self.setupUi(self)

    self.workflowTemplateManager = WorkflowTemplateManager(currentPath)
    self.workflowTemplate = WorkflowTemplate()

    self.btnSave = self.buttonBox.button(QDialogButtonBox.Save)
    self.btnClose = self.buttonBox.button(QDialogButtonBox.Close)

    self.btnNew.clicked.connect(self.newWorkflow)
    self.btnRemove.clicked.connect(self.removeWorkflow)
    self.leName.textEdited.connect(self.templateModified)
    self.textDescription.textChanged.connect(self.templateModified)
    self.cmbWorkflow.currentIndexChanged.connect(self.workflowChanged)

    self.buttonBox.accepted.disconnect(self.accept)
    self.btnSave.clicked.connect(self.saveTemplate)

    self.manageGui()

  def manageGui(self):
    self.btnRemove.setEnabled(False)
    self.reloadTemplatesList()
    self.btnSave.setEnabled(False)

  def reloadTemplatesList(self):
    self.cmbWorkflow.clear()
    self.cmbWorkflow.addItems(self.workflowTemplateManager.getTemplateList())

  def newWorkflow(self):
    if self.btnSave.isEnabled() and QMessageBox.question(None,
                                                         self.tr("Metatools"),
                                                         self.tr("Template contains unsaved data. Create new template without saving?"),
                                                         QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
      return
    self.clearFormFields()
    self.workflowTemplate = WorkflowTemplate()
    self.btnSave.setEnabled(False)

  def removeWorkflow(self):
    if self.workflowTemplate.name:
      self.workflowTemplateManager.removeTemplate(self.workflowTemplate.name)
      self.reloadTemplatesList()

    if self.cmbWorkflow.count() == 0:
      self.clearFormFields()
      self.btnSave.setEnabled(False)

  # enable save button when templated edited
  def templateModified(self):
    self.btnSave.setEnabled(True)

  def workflowChanged(self):
    templateName = self.cmbWorkflow.currentText()
    if templateName == "":
      self.workflowTemplate = WorkflowTemplate()
      self.btnRemove.setEnabled(False)
      return

    self.workflowTemplate = self.workflowTemplateManager.loadTemplate(templateName)
    self.templateToForm(self.workflowTemplate)
    self.btnSave.setEnabled(False)
    self.btnRemove.setEnabled(True)

  def saveTemplate(self):
    template = self.templateFromForm()

    # check template attrs
    if template.name is None or template.name == "":
      QMessageBox.warning(self,
                          self.tr("Manage workflows"),
                          self.tr("The name of the workflow must be specified!")
                         )
      return

    # try save template
    try:
      # first delete old template
      if self.workflowTemplate.name and self.workflowTemplate.name != "":
        self.workflowTemplateManager.removeTemplate(self.workflowTemplate.name)
      # save new version
      self.workflowTemplateManager.saveTemplate(template)
    except:
      QMessageBox.warning(self,
                          self.tr("Manage workflows"),
                          self.tr("Template can't be saved: ") + unicode(sys.exc_info()[1])
                         )
      return

    # reload form
    self.reloadTemplatesList()

    # set combobox item
    index = self.cmbWorkflow.findText(template.name)
    if index != -1:
      self.cmbWorkflow.setCurrentIndex(index)

    self.btnSave.setEnabled(False)

  def clearFormFields(self):
    self.leName.clear()
    self.textDescription.clear()

  # populate form with template data
  def templateToForm(self, template):
    self.leName.setText(template.name or "")
    self.textDescription.setPlainText(template.description or "")

  # create template from entered values
  def templateFromForm(self):
    template = WorkflowTemplate()
    template.name = self.leName.text()
    template.description = self.textDescription.toPlainText()
    return template

  def reject(self):
    if self.btnSave.isEnabled() and QMessageBox.question(None,
                                                         self.tr("Metatools"),
                                                         self.tr("Template contains unsaved data. Close the window without saving?"),
                                                         QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
      return
    QDialog.reject(self)

  def accept(self):
    QDialog.accept(self)
