#---------------------------------------------------------------------#
# Author: Bruce Evans, brucein3d@gmail.com
# Copyright 2020 Bruce Evans
# Trebuchet Launcher
#---------------------------------------------------------------------#

# TODO listwidget size
# TODO headers
# TODO .ini writing

import os
import sys
import json
import psutil
import subprocess
import configparser
import webbrowser
import qdarkstyle
import qdarkgraystyle
import ExtractIcon
from PySide2 import QtCore, QtGui, QtWidgets


class Launcher:

    def __init__(self, controller):

        # globals
        self.controller = controller
        self.applicationPath = self._getApplicationPath()
        self.apps = self._getAppList()
        self.launchButtons = []

        # default tags
        self.tags = [
            "Art",
            "Code",
            "Games",
            "Media",
            "Productivity",
            "Web"
        ]

        # setup methods
        self._initApp()
        self._initTags()
        self._setupSettings()
        self._setupUi()
        self._connectWidgets()

        # init buttons
        self._initLauncherButtons()

        self.mainIcon = QtGui.QIcon(self.applicationPath + "\\resources\\icons\\launcher_icon.png")

    def _initApp(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

    def _setupUi(self):

        self.launcherIcon = QtGui.QIcon(self.applicationPath + "\\resources\\icons\\launcher_icon.png")
        self.rightClickMenu = QtWidgets.QMenu()

        # Right click menu
        self.trayContextMenu = QtWidgets.QMenu()

        self.actionAddApplication = self.trayContextMenu.addAction("Add Application")
        self.actionAddApplication.setIcon(QtGui.QIcon(
            self.applicationPath + "\\resources\\icons\\icon_add.png"))
        
        self.actionSettings = self.trayContextMenu.addAction("Settings")
        self.actionSettings.setIcon(QtGui.QIcon(
            self.applicationPath + "\\resources\\icons\\icon_settings.png"))

        self.actionAbout = self.trayContextMenu.addAction("About")
        self.actionAbout.setIcon(QtGui.QIcon(
            self.applicationPath + "\\resources\\icons\\icon_info.png"))
        self.actionAbout.triggered.connect(self._showAboutMenu)

        self.actionClose = self.trayContextMenu.addAction("Close Launcher")
        self.actionClose.setIcon(QtGui.QIcon(
            self.applicationPath + "\\resources\\icons\\icon_close.png"))
        self.actionClose.triggered.connect(self._closeApp)

        # Tray icon

        self.trayIcon = QtWidgets.QSystemTrayIcon()
        self.trayIcon.setIcon(self.launcherIcon)
        self.trayIcon.setContextMenu(self.trayContextMenu)
        self.trayIcon.show()

        # Launcher menu

        self.launcherMenu = QtWidgets.QMenu()

        # Add application menu

        self.addApplicationMenu = QtWidgets.QDialog()

        # Rename app menu

        self.renameAppMenu = QtWidgets.QDialog()

        # Edit tag menu

        self.renameTagMenu = QtWidgets.QDialog()

        # Settings menu

        self.settingsMenu = QtWidgets.QDialog()

        # Delete tag warning

        self.tagWarning = QtWidgets.QDialog()

        # About menu
        
        self.aboutMenu = QtWidgets.QDialog()

    def _connectWidgets(self):
        self.trayIcon.activated.connect(self._onTrayActivated)
        self.actionAddApplication.triggered.connect(self._addApplication)
        self.actionSettings.triggered.connect(self._showSettingsMenu)

    def _getApplicationPath(self):
        if getattr(sys, 'frozen', False):
            # format for mac?
            return os.path.dirname(sys.executable)
        elif __file__:
            # TODO Update this for mac path
            scriptPath = os.path.dirname(__file__)
            projectDirectory = scriptPath.split("src")[0]
            return projectDirectory

    def _setupSettings(self):
        # grab settings on startup 
        config = configparser.ConfigParser()
        config.read(self.applicationPath + "\\resources\\settings.ini")

        useHeader = config.get('SETTINGS', 'useHeader')
        if useHeader == 'false':
            self.useHeader = False
        else:
            self.useHeader = True

        self.theme = config.get('SETTINGS', 'theme')

        if self.theme == 'darkblue':
            self.app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
        else:
            light = ""
            self.app.setStyleSheet(light)


    def _updateSettings(self, useHeader, theme):
        config = configparser.ConfigParser()
        config.read(self.applicationPath + "\\resources\\settings.ini")

        if useHeader == False:
            config.set('SETTINGS', 'useHeader', 'false')
        else:
            config.set('SETTINGS', 'useHeader', 'true')

        # TODO theme
        config.set('SETTINGS', 'theme', theme)

    def _onTrayActivated(self, reason):
        if reason == self.trayIcon.Trigger:
            self.launcherMenu.show()
            trayGeometry = self.trayIcon.geometry()
            launcherMenuGeometry = self.launcherMenu.frameGeometry()
            centerPoint = trayGeometry.center()
            launcherMenuGeometry.moveBottomLeft(centerPoint)
            self.launcherMenu.move(launcherMenuGeometry.topLeft())
            self.launcherMenu.show()

    def _showAddApplicationMenu(self, appPath):
        self.addApplicationMenu.setWindowTitle("Add an application")
        self.addApplicationMenu.setWindowIcon(self.mainIcon)

        # Create the button with a default tag
        launchButton = LauncherButton(self.trayIcon, appPath, self.applicationPath, "Application") # temp tag

        mainLayout = QtWidgets.QVBoxLayout()

        labelName = QtWidgets.QLabel("Name:")
        lineName = QtWidgets.QLineEdit()
        lineName.setText(launchButton.buttonName)
        layoutName = QtWidgets.QHBoxLayout()
        layoutName.addWidget(labelName)
        layoutName.addWidget(lineName)

        labelTag = QtWidgets.QLabel("Tag:")
        checkBoxTag = QtWidgets.QComboBox()

        for tag in self.tags:
            checkBoxTag.addItem(tag)

        layoutTag = QtWidgets.QHBoxLayout()
        layoutTag.addWidget(labelTag)
        layoutTag.addWidget(checkBoxTag)

        labelTag = QtWidgets.QLabel("New tag:")
        lineEditTag = QtWidgets.QLineEdit()

        layoutNewTag = QtWidgets.QHBoxLayout()
        layoutNewTag.addWidget(labelTag)
        layoutNewTag.addWidget(lineEditTag)

        btnLayout = QtWidgets.QHBoxLayout()
        btnAccept = QtWidgets.QPushButton("Ok")

        btnAccept.clicked.connect(lambda: self._addApplicationAccept(launchButton, lineName.text(), str(checkBoxTag.currentText()), lineEditTag.text()))
        btnCancel = QtWidgets.QPushButton("Cancel")

        btnLayout.addWidget(btnAccept)
        btnLayout.addWidget(btnCancel)

        # addButtonAccept menu will create the final name, tag, and add it to the list
        
        mainLayout.addLayout(layoutName)
        mainLayout.addLayout(layoutTag)
        mainLayout.addLayout(layoutNewTag)
        mainLayout.addLayout(btnLayout)

        self.addApplicationMenu.setLayout(mainLayout)
        self.addApplicationMenu.show()

    def _addApplication(self):

        fileDialog = QtWidgets.QFileDialog()
        appPath, _ = fileDialog.getOpenFileName(
            None,
            "Choose an application to add",
            "C:\\",
            "Applications (*.exe)"
        )

        fileDialog.setFixedSize(640, 480)

        if appPath != "":
            self._showAddApplicationMenu(appPath)

    def _addApplicationAccept(self, button, name, dropdown, tag):

        # Clear window
        del self.addApplicationMenu
        self.addApplicationMenu = QtWidgets.QDialog()
        self.addApplicationMenu.close()

        # Update name and tag

        if tag == "":
            button.updateTag(dropdown)
        else:
            button.updateTag(tag)
        button.updateName(name)

        # check if tag exitst, if not add it
        tagExists = False
        for t in self.tags:
            if tag == t:
                tagExists = True
                break

        if not tagExists and tag != "":
            self.tags.append(tag)

        # write to JSON
    
        appList = self._readAppsFromJson()
        newEntry = {
            'name': button.buttonName,
            'directory': button.buttonAppPath,
            'exe': button.exeFile,
            'icon': button.icon,
            'tag': button.tag
        }
        appList.append(newEntry)
        self._writeAppList(appList, self.applicationPath + "\\resources\\apps.json")

        # Init buttons
        self._initLauncherButtons()

    def _showSettingsMenu(self):

        # clear old menu
        del self.settingsMenu
        self.settingsMenu = QtWidgets.QDialog()
        self.settingsMenu.close()

        self.settingsMenu.setWindowTitle("Settings")
        self.settingsMenu.setWindowIcon(self.mainIcon)
        # useHeader checkbox
        # checkBoxUseHeader = QtWidgets.QCheckBox("Use Headers")
        # checkBoxUseHeader.stateChanged.connect(lambda:self._setUseHeaders(checkBoxUseHeader.isChecked()))

        labelApps = QtWidgets.QLabel("Modify Apps")
        listApps = QtWidgets.QListWidget()
        for button in self.launchButtons:
            newItem = QtWidgets.QListWidgetItem(button.buttonName)
            listApps.addItem(newItem)

        btnRenameApp = QtWidgets.QPushButton("Rename App")
        btnRenameApp.clicked.connect(lambda : self._renameApplicationMenu(listApps))
        btnDeleteApp = QtWidgets.QPushButton("Delete App")
        btnDeleteApp.clicked.connect(lambda : self._removeApplication(listApps))
        
        layoutAppButtons = QtWidgets.QHBoxLayout()
        layoutAppButtons.addWidget(btnRenameApp)
        layoutAppButtons.addWidget(btnDeleteApp)

        labelTags = QtWidgets.QLabel("Modify Tags")
        listTags = QtWidgets.QListWidget()
        for tag in self.tags:
            newItem = QtWidgets.QListWidgetItem(tag)
            listTags.addItem(newItem)

        btnRenameTag = QtWidgets.QPushButton("Rename Tag")
        btnRenameTag.clicked.connect(lambda : self._renameTagMenu(listTags))
        btnDeleteTag = QtWidgets.QPushButton("Delete Tag")
        btnDeleteTag.clicked.connect(lambda : self._removeTag(listTags))

        layoutTagButtons = QtWidgets.QHBoxLayout()
        layoutTagButtons.addWidget(btnRenameTag)
        layoutTagButtons.addWidget(btnDeleteTag)

        # theme dropdown
        labelTheme = QtWidgets.QLabel("Choose Theme: ")
        dropDownTheme = QtWidgets.QComboBox()
        dropDownTheme.addItem("Dark Blue")
        dropDownTheme.addItem("Dark Gray")
        dropDownTheme.addItem("Light")

        dropDownTheme.currentIndexChanged.connect(self._setTheme)

        themeLayout = QtWidgets.QHBoxLayout()
        themeLayout.addWidget(labelTheme)
        themeLayout.addWidget(dropDownTheme)

        listLayout = QtWidgets.QVBoxLayout()
        listLayout.addWidget(labelApps)
        listLayout.addWidget(listApps)
        listLayout.addLayout(layoutAppButtons)
        listLayout.addWidget(labelTags)
        listLayout.addWidget(listTags)
        listLayout.addLayout(layoutTagButtons)

        btnAccept = QtWidgets.QPushButton("OK")
        btnAccept.clicked.connect(lambda : self._acceptDialog(self.settingsMenu))

        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.addWidget(btnAccept)

        mainLayout = QtWidgets.QVBoxLayout()
        # mainLayout.addWidget(checkBoxUseHeader)
        mainLayout.addLayout(listLayout)
        mainLayout.addLayout(themeLayout)
        mainLayout.addLayout(btnLayout)

        self.settingsMenu.setLayout(mainLayout)
        self.settingsMenu.show()

    ## Settings methods ##

    def _removeApplication(self, listWidget):
        selection = listWidget.currentItem()
        if not selection:
            return
        appName = selection.text()

        appList = self._readAppsFromJson()
        for entry in appList:
            if entry.get("name") == appName:
                appList.remove(entry)
        self._writeAppList(appList, self.applicationPath + "\\resources\\apps.json")

        # remove the list item
        listWidget.takeItem(listWidget.row(selection))

        self._initLauncherButtons()
    
    def _renameApplicationMenu(self, listWidget):

        # clear menu
        del self.renameAppMenu

        self.renameAppMenu = QtWidgets.QDialog()
        self.renameAppMenu.setWindowTitle("Rename an App")
        self.renameAppMenu.setWindowIcon(self.mainIcon)

        labelNewName = QtWidgets.QLabel("New Name: ")
        lineEditName = QtWidgets.QLineEdit()

        layoutNewName = QtWidgets.QHBoxLayout()
        layoutNewName.addWidget(labelNewName)
        layoutNewName.addWidget(lineEditName)

        btnAccept = QtWidgets.QPushButton("Accept")
        btnCancel = QtWidgets.QPushButton("Cancel")

        btnAccept.clicked.connect(lambda : self._renameApplication(self.renameAppMenu, listWidget, lineEditName.text()))
        btnCancel.clicked.connect(lambda : self._cancelDialog(self.renameAppMenu))

        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.addWidget(btnAccept)
        btnLayout.addWidget(btnCancel)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(layoutNewName)
        mainLayout.addLayout(btnLayout)
        self.renameAppMenu.setLayout(mainLayout)

        self.renameAppMenu.show()

    def _renameApplication(self, dialog, listWidget, newName):
        # update the apps name in the json file and list widget
        selection = listWidget.currentItem()
        if not selection:
            return

        appName = selection.text()
        appList = self._readAppsFromJson()
        for entry in appList:
            if entry.get("name") == appName:
                entry["name"] = newName
        self._writeAppList(appList, self.applicationPath + "\\resources\\apps.json")

        selection.setText(newName)

        # initLaunchButtons
        self._initLauncherButtons()

        dialog.accept()

    def _removeTag(self, listWidget):

        warning = "Deleting a tag will delete all buttons\nassociated with that tag. Is that OK?"
        warningMessageBox = QtWidgets.QMessageBox()
        reply = warningMessageBox.question(self.settingsMenu, 'Be Careful!', warning, warningMessageBox.Ok | warningMessageBox.Cancel)

        if reply == warningMessageBox.Ok:
            selection = listWidget.currentItem()
            if not selection:
                return
            tag = selection.text()

            appList = self._readAppsFromJson()
            for entry in appList:
                if entry.get("tag") == tag:
                    appList.remove(entry)
            self._writeAppList(appList, self.applicationPath + "\\resources\\apps.json")
            for t in self.tags:
                if t == tag:
                    self.tags.remove(t)
            
            listWidget.takeItem(listWidget.row(selection))

            self._initLauncherButtons()
        else:
            return

    def _renameTagMenu(self, listWidget):

        # clear menu
        del self.renameTagMenu

        self.renameTagMenu = QtWidgets.QDialog()
        self.renameTagMenu.setWindowTitle("Rename a Tag")
        self.renameTagMenu.setWindowIcon(self.mainIcon)

        labelNewName = QtWidgets.QLabel("New Name: ")
        lineEditName = QtWidgets.QLineEdit()

        layoutNewName = QtWidgets.QHBoxLayout()
        layoutNewName.addWidget(labelNewName)
        layoutNewName.addWidget(lineEditName)

        btnAccept = QtWidgets.QPushButton("Accept")
        btnCancel = QtWidgets.QPushButton("Cancel")

        btnAccept.clicked.connect(lambda : self._renameTag(self.renameTagMenu, listWidget, lineEditName.text()))
        btnCancel.clicked.connect(lambda : self._cancelDialog(self.renameTagMenu))

        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.addWidget(btnAccept)
        btnLayout.addWidget(btnCancel)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(layoutNewName)
        mainLayout.addLayout(btnLayout)
        self.renameTagMenu.setLayout(mainLayout)

        self.renameTagMenu.show()
    
    def _renameTag(self, dialog, listWidget, newTag):
        selection = listWidget.currentItem()
        if not selection:
            return
        # update name in self.tags
        oldTag = selection.text()
        for tag in self.tags:
            if tag == oldTag:
                self.tags.remove(tag)
                # tag = newTag
        self.tags.append(newTag)
        self.tags = sorted(self.tags)
        # for each app with the old tag, update it
        appList = self._readAppsFromJson()
        for entry in appList:
            if entry.get("tag") == oldTag:
                entry["tag"] = newTag
        self._writeAppList(appList, self.applicationPath + "\\resources\\apps.json")
        selection.setText(newTag)
        self._initLauncherButtons()
        dialog.accept()

    # TODO last settings

    def _setUseHeaders(self, useHeader):
        self.useHeader = useHeader

    def _initTags(self):
        appList = self._readAppsFromJson()

        for app in appList:
            # check defaults
            match = False
            for tag in self.tags:
                if tag == app.get("tag"):
                    match = True
                    break
            # add to self.tags
            if not match:
                self.tags.append(app.get("tag"))

    ## Button specific methods ##

    def _initLauncherButtons(self):

        # clear old buttons
        self.launchButtons.clear()

        # clear folder actions
        for action in self.launcherMenu.actions():
            self.launcherMenu.removeAction(action)

        # read new from json
        jsonAppsList = self._readAppsFromJson()
        # sortedAppsByTag = self._getTagsFromJson(jsonAppsList)

        # sort by name within tag
        tagLists = []

        self.tags = sorted(self.tags)

        for tag in self.tags:
            tagList = []
            tagLists.append(tagList)

        for i in range(len(self.tags)):
            try:
                for app in jsonAppsList:
                    t = app.get("tag")
                    if t == self.tags[i]:
                        tagLists[i].append(app)
            except KeyError:
                print("No key found")

        # Sort by name

        for i in range(len(tagLists)):
            tagLists[i] = sorted(tagLists[i], key=lambda x: x['name'])

        spacers = []

        for i in range(len(tagLists)):
            spacers.append(-1)
            for j in range(len(tagLists[i])):
                button = LauncherButton(self.trayIcon, tagLists[i][j].get("directory"), self.applicationPath, tagLists[i][j].get("tag"))
                button.updateName(tagLists[i][j].get("name"))
                self.launchButtons.append(button)
                spacers.append(button)
        
        for i in range(len(spacers)):
            if spacers[i] == -1:
                # TODO header
                if self.useHeader:
                    print("Adding header")
                    # self.launcherMenu.addSection("Test Section")
                self.launcherMenu.addSeparator()
            else:
                action = self.launcherMenu.addAction(spacers[i].buttonName)
                action.setIcon(QtGui.QIcon(
                    spacers[i].icon
                ))
                action.triggered.connect(spacers[i].launch)

        # Last add the folder button
        self.launcherMenu.addSeparator()
        folderAction = self.launcherMenu.addAction("Explorer Window")
        folderAction.triggered.connect(self._openExplorerWindow)
        folderAction.setIcon(QtGui.QIcon(self.applicationPath + "\\resources\\icons\\icon_folder.png"))

    ## Tag specific methods

    def _getTagsFromJson(self, appList):  # get existing tags

        tagList = []

        if len(appList) > 0:
            currentTag = appList[0]["tag"]
            for i in range(len(appList)):
                if i != 0 and currentTag != appList[i]["tag"]:
                    tagList.append(currentTag)

        else:
            print("No existing apps in the JSON file")

        return sorted(tagList)

    ## JSON methods ##

    def _getAppList(self):
        return self.applicationPath + "\\resources\\apps.json"

    def _readAppsFromJson(self):
        #  Get buttons from json file
        jsonPath = self.applicationPath + "\\resources\\apps.json"

        with open(jsonPath, 'r') as j:
            appsList = json.load(j)

        appsList = sorted(appsList, key=lambda i: i['tag'])

        return appsList

    def _writeAppList(self, apps, jsonFile):
        with open(jsonFile, 'w') as jFile:
            json.dump(apps, jFile, indent=4)

    ## Explorer Window ##

    def _openExplorerWindow(self):
        desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
        subprocess.Popen('explorer ' + desktop)

    ## Settings ##

    def _setTheme(self, themeIndex):
        if themeIndex == 0:
            self.theme = "darkblue"
            self.app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
        elif themeIndex == 1:
            self.theme = "darkgray"
            self.app.setStyleSheet(qdarkgraystyle.load_stylesheet())
        else:
            self.theme = "light"
            light = ""
            self.app.setStyleSheet(light)
            print("changing to light")

    ## About ##

    def _showAboutMenu(self):

        #clear menu
        del self.aboutMenu

        self.aboutMenu = QtWidgets.QDialog()
        self.aboutMenu.setWindowTitle("About Trebuchet")
        self.aboutMenu.setWindowIcon(self.mainIcon)

        labelThanks = QtWidgets.QLabel("Thanks for supporting Trebuchet!")
        contact = "If you have any questions, suggestions, or bugs feel free to email me."
        email = "brucein3d@gmail.com"
        website = "<a href='https://www.brucein3d.com/trebuchet'>www.brucein3d.com</a>"

        mainLayout = QtWidgets.QVBoxLayout()

        labelContact = QtWidgets.QLabel(contact)
        labelEmail = QtWidgets.QLabel(email)
        labelWebsite = QtWidgets.QLabel(website)
        labelWebsite.setOpenExternalLinks(True)

        mainLayout.addWidget(labelThanks)
        mainLayout.addWidget(labelContact)
        mainLayout.addWidget(labelEmail)
        mainLayout.addWidget(labelWebsite)

        self.aboutMenu.setLayout(mainLayout)

        self.aboutMenu.show()

    ## Run and close ##

    def _acceptDialog(self, dialog):
        # update settings
        self._updateSettings(False, self.theme)
        dialog.accept()

    def _cancelDialog(self, dialog):
        dialog.reject()

    def _closeApp(self):
        QtCore.QCoreApplication.exit()

    def run(self):
        sys.exit(self.app.exec_())


class LauncherButton(QtWidgets.QAction):
    def __init__(self, trayIcon, buttonAppPath, trebuchetPath, tag, *args, **kwargs):
        QtWidgets.QAction.__init__(self, *args, **kwargs)
        # Globals
        self.trayIcon = trayIcon
        self.buttonAppPath = buttonAppPath
        self.trebuchetPath = trebuchetPath
        self.tag = tag

        # Init
        self._setupLauncherButton()

    def _setupLauncherButton(self):
        self.exeFile = self._getExe(self.buttonAppPath)
        self.buttonName = self._getAppName(self.exeFile)
        self.icon = self._getIcon(self.buttonAppPath, self.trebuchetPath)
        self.triggered.connect(self.launch)

    def _getExe(self, path):
        # TODO mac solution
        exe = os.path.split(path)[1]
        return exe

    def _getAppName(self, exeOrApp):
        # remove extension
        # TODO mac
        name = exeOrApp.replace(".exe", "")
        return name

    def _getIcon(self, exePath, appPath):

        icon = self.trebuchetPath + "\\resources\\icons\\icon_" + self.buttonName + ".png"

        if not (os.path.exists(icon)):
            # extract the exe icon and place it at the _icon path
            # TODO mac solution
            ExtractIcon.getIcon(exePath, icon)

        return icon

    def launch(self):
        # launch using subprocess call
        if self.exeFile not in (p.name() for p in psutil.process_iter()):
            os.startfile(self.buttonAppPath)
        else:
            # TODO Icon image?
            self.trayIcon.showMessage("Oops!", self.exeFile + " is already running")
            return

    def updateName(self, newName):
        self.buttonName = newName

    def updateTag(self, newTag):
        self.tag = newTag
