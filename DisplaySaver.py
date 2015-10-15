#Author-Patrick Rainsberry
#Description-Save and retrieve display conditions of the model



import adsk.core, adsk.fusion, traceback

from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

from os.path import expanduser
import os



# global event handlers referenced for the duration of the command
handlers = []

menu_panel = 'InspectPanel'
commandResources = './resources'

commandId = 'displaySave'
commandName = 'Display Saver'
commandDescription = 'Manage Display of Parts'

DS_CmdId = 'DS_CmdId'
cmdIds = [DS_CmdId]

def commandDefinitionById(id):
    app = adsk.core.Application.get()
    ui = app.userInterface
    if not id:
        ui.messageBox('commandDefinition id is not specified')
        return None
    commandDefinitions_ = ui.commandDefinitions
    commandDefinition_ = commandDefinitions_.itemById(id)
    return commandDefinition_

def commandControlByIdForNav(id):
    app = adsk.core.Application.get()
    ui = app.userInterface
    if not id:
        ui.messageBox('commandControl id is not specified')
        return None
    toolbars_ = ui.toolbars
    toolbarNav_ = toolbars_.itemById('NavToolbar')
    toolbarControls_ = toolbarNav_.controls
    toolbarControl_ = toolbarControls_.itemById(id)
    return toolbarControl_

def commandControlByIdForPanel(id):
    app = adsk.core.Application.get()
    ui = app.userInterface
    if not id:
        ui.messageBox('commandControl id is not specified')
        return None
    workspaces_ = ui.workspaces
    modelingWorkspace_ = workspaces_.itemById('FusionSolidEnvironment')
    toolbarPanels_ = modelingWorkspace_.toolbarPanels
    toolbarPanel_ = toolbarPanels_.item(0)
    toolbarControls_ = toolbarPanel_.controls
    toolbarControl_ = toolbarControls_.itemById(id)
    return toolbarControl_

def destroyObject(uiObj, tobeDeleteObj):
    if uiObj and tobeDeleteObj:
        if tobeDeleteObj.isValid:
            tobeDeleteObj.deleteMe()
        else:
            uiObj.messageBox('tobeDeleteObj is not a valid object')
                    
def writeXML(tree, newState, fileName):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    # Get the root component of the active design.
    rootComp = adsk.fusion.Component.cast(design.rootComponent)
    
    # Get XML Root node
    root = tree.getroot()
    
    # Create a new Stte in the file
    state = SubElement( root, 'state', name=newState )
    
    # Get All occurences inside the root component
    allOccurences = rootComp.allOccurrences
    
    for occurence in allOccurences:
            if occurence.isLightBulbOn:                               
                SubElement( state, 'occurance', name=occurence.fullPathName, hide = 'show')
            else:
                SubElement( state, 'occurance', name=occurence.fullPathName, hide = 'hide')
    
    tree.write(fileName)

def openXML(tree, state):
    
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    
    # Get the root component of the active design.
    rootComp = adsk.fusion.Component.cast(design.rootComponent)
    allOccurences = rootComp.allOccurrences
    
    # Get XML Root node
    root = tree.getroot()

    for occurence in allOccurences:
        test = root.find('state[@name="%s"]/occurance[@name="%s"]' % (state, occurence.fullPathName))
        if test is not None:
            if test.get('hide') == 'hide':
                occurence.isLightBulbOn = False
            else:
                occurence.isLightBulbOn = True
    
def getFileName():
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        doc = app.activeDocument
        
        home = expanduser("~")
        home += '/displaySaver/'
        
        if not os.path.exists(home):
            os.makedirs(home)
        
        fileName = home  + doc.name[0:doc.name.rfind(' v')] + '.xml'
        if not os.path.isfile(fileName):
            new_file = open( fileName, 'w' )                        
            new_file.write( '<?xml version="1.0"?>' )
            new_file.write( "<displaySaves /> ")
            new_file.close()
        
        return fileName
    
    except:
        if ui:
            ui.messageBox('Panel command created failed:\n{}'
            .format(traceback.format_exc()))

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        class DS_InputChangedHandler(adsk.core.InputChangedEventHandler):
            def __init__(self):
                super().__init__()
            def notify(self, args):
                try:
                    command = args.firingEvent.sender
                    inputs = command.commandInputs
                    if inputs.itemById('save').value:
                        inputs.itemById('currentState').isVisible = False
                        inputs.itemById('newName').isEnabled = True
                    else:
                        inputs.itemById('currentState').isVisible = True
                        inputs.itemById('newName').isEnabled = False

                except:
                    if ui:
                        ui.messageBox('Input changed event failed: {}').format(traceback.format_exc())
        
        # Handle the input changed event.        
        class DS_executePreviewHandler(adsk.core.CommandEventHandler):
            def __init__(self):
                super().__init__()
            def notify(self, args):
                app = adsk.core.Application.get()
                ui  = app.userInterface
                try:
                    command = args.firingEvent.sender
                    inputs = command.commandInputs
                    state = inputs.itemById('currentState').selectedItem.name
                    if state != 'Current' and not inputs.itemById('save').value:
                        fileName = getFileName()                    
                        tree = ElementTree.parse(fileName)
                        openXML(tree, state)
                    
                except:
                    if ui:
                        ui.messageBox('command executed failed:\n{}'
                        .format(traceback.format_exc()))                
        class DS_CreatedHandler(adsk.core.CommandCreatedEventHandler):
            def __init__(self):
                super().__init__() 
            def notify(self, args):
                try:
                    cmd = args.command
                    onExecute = DS_ExecuteHandler()
                    cmd.execute.add(onExecute)
                    onChange = DS_InputChangedHandler()
                    cmd.inputChanged.add(onChange)
                    onUpdate = DS_executePreviewHandler()
                    cmd.executePreview.add(onUpdate)
                    
                    # keep the handler referenced beyond this function
                    handlers.append(onExecute)  
                    handlers.append(onChange)
                    handlers.append(onUpdate)
                    
                    fileName = getFileName()                    
                    tree = ElementTree.parse(fileName)
                    root = tree.getroot()
                    
                    inputs = cmd.commandInputs
                    
                    dropDown = inputs.addDropDownCommandInput('currentState', 'Select Saved Display:', adsk.core.DropDownStyles.TextListDropDownStyle)
                    dropDownItems = dropDown.listItems
                    
                    dropDownItems.add('Current', True)
                    
                    for state in root.findall('state'):
                        dropDownItems.add(state.get('name'), False,)
                        
                    inputs.addBoolValueInput('save', 'Save current display condition?', True)
                    inputs.addStringValueInput('newName', 'New Display Name:', 'New Display') 
                         
                        
                except:
                    if ui:
                        ui.messageBox('Panel command created failed:\n{}'
                        .format(traceback.format_exc()))     

        class DS_ExecuteHandler(adsk.core.CommandEventHandler):
            def __init__(self):
                super().__init__()
            def notify(self, args):
                try:  
                    command = args.firingEvent.sender
                    inputs = command.commandInputs
                    state = inputs.itemById('currentState').selectedItem.name
                    fileName = getFileName()                    
                    tree = ElementTree.parse(fileName)
                    if inputs.itemById('save').value:
                        writeXML(tree, inputs.itemById('newName').value, fileName)
                    else:
                        openXML(tree, state)  
                    
                    
                except:
                    if ui:
                        ui.messageBox('command executed failed:\n{}'
                        .format(traceback.format_exc()))   
                                              
        # Get the UserInterface object and the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions

        #global showAllBodiesCmdId
        #otherCmdDefs = [showAllCompsCmdId, showHiddenBodiesCmdId, showHiddenCompsCmdId]
        # add a command button on Quick Access Toolbar
        toolbars_ = ui.toolbars
        navBar = toolbars_.itemById('NavToolbar')
        toolbarControlsNAV = navBar.controls
        
        DS_Control = toolbarControlsNAV.itemById(DS_CmdId)
        if not DS_Control:
            DS_cmdDef = cmdDefs.itemById(DS_CmdId)
            if not DS_cmdDef:
                # commandDefinitionNAV = cmdDefs.addSplitButton(showAllBodiesCmdId, otherCmdDefs, True)
                DS_cmdDef = cmdDefs.addButtonDefinition(DS_CmdId, 'Display Saver', 'Manage Display of Bodies and Components',commandResources)
            onCommandCreated = DS_CreatedHandler()
            DS_cmdDef.commandCreated.add(onCommandCreated)
            # keep the handler referenced beyond this function
            handlers.append(onCommandCreated)
            DS_Control = toolbarControlsNAV.addCommand(DS_cmdDef)
            DS_Control.isVisible = True

        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        objArrayNav = []
        
        for cmdId in cmdIds:
            commandControlNav_ = commandControlByIdForNav(cmdId)
            if commandControlNav_:
                objArrayNav.append(commandControlNav_)
    
            commandDefinitionNav_ = commandDefinitionById(cmdId)
            if commandDefinitionNav_:
                objArrayNav.append(commandDefinitionNav_)
            
        for obj in objArrayNav:
            destroyObject(ui, obj)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
