import adsk.core, adsk.fusion
from .commands import PaletteCommand  # Import the NEW command file
from .lib import fusionAddInUtils as futil
from . import config

def run(context):
    try:
        # Just run the start function of our new single command file
        PaletteCommand.start()
        
        # Add the button to the UI (Solid Tab -> Insert Panel)
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        workspace = ui.workspaces.itemById(config.DEFAULT_WORKSPACE_ID)
        tab = workspace.toolbarTabs.itemById(config.DEFAULT_TAB_ID)
        panel = tab.toolbarPanels.itemById(config.DEFAULT_PANEL_ID)
        
        # Add the button if it doesn't exist on the panel
        # Note: PaletteCommand.start() created the Definition, 
        # this adds the Control to the panel
        cmdDef = ui.commandDefinitions.itemById(config.SHOW_EDIT_COMMAND_ID)
        if cmdDef:
            control = panel.controls.addCommand(cmdDef)
            # Add the icon to the toolbar
            control.isPromoted = True

    except:
        futil.handle_error('run')

def stop(context):
    try:
        # Clean up the palette and command
        PaletteCommand.stop()
        
        # Remove the button from the panel
        app = adsk.core.Application.get()
        ui = app.userInterface
        workspace = ui.workspaces.itemById(config.DEFAULT_WORKSPACE_ID)
        tab = workspace.toolbarTabs.itemById(config.DEFAULT_TAB_ID)
        panel = tab.toolbarPanels.itemById(config.DEFAULT_PANEL_ID)
        
        if panel:
            cntrl = panel.controls.itemById(config.SHOW_EDIT_COMMAND_ID)
            if cntrl: cntrl.deleteMe()
            
        futil.clear_handlers()

    except:
        futil.handle_error('stop')