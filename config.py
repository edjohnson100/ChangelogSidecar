"""
Global configuration and constants for the add-in.
"""
import os
import json

# Flag that indicates to run in Debug mode or not.
DEBUG = True

# Gets the name of the add-in from the name of the folder the py file is in.
# This will automatically become 'ChangelogSidecar' after the folder rename.
ADDIN_NAME = os.path.basename(os.path.dirname(__file__))
COMPANY_NAME = 'EdJ' 

# ==============================================================================
# Settings Configuration
# ==============================================================================
DEFAULT_WORKSPACE_ID = 'FusionSolidEnvironment' # Design Workspace
DEFAULT_TAB_ID = 'SolidTab'                 
DEFAULT_PANEL_ID = 'InsertPanel'

# ==============================================================================
# Resource Paths
# ==============================================================================
RESOURCES_ROOT = 'resources'

def get_resource_folder(folder_name=''):
    # Defaults to the root resources folder if no name is provided
    return os.path.join(RESOURCES_ROOT, folder_name)

# ==============================================================================
# Palette Constants
# ==============================================================================
PALETTE_ID = f'{COMPANY_NAME}_{ADDIN_NAME}_Palette'
PALETTE_NAME = 'Changelog Sidecar' 

# Point to the file inside the resources folder
PALETTE_URL = './resources/changelog_ui.html'

# ==============================================================================
# Command Constants
# ==============================================================================

# --- NEW DATA KEYS (Clean Slate) ---
# These will now generate as:
# EdJ_ChangelogSidecar_Group
# EdJ_ChangelogSidecar_Data
CHANGELOG_GROUP_KEY = f'{COMPANY_NAME}_{ADDIN_NAME}_Group'
CHANGELOG_NAME_KEY = f'{COMPANY_NAME}_{ADDIN_NAME}_Data'
ARCHIVE_LOG_PREFIX = 'archive_' 

# --- Command: Open Changelog Palette ---
SHOW_EDIT_COMMAND_ID = f'{COMPANY_NAME}_{ADDIN_NAME}_ShowChangelog'
SHOW_EDIT_COMMAND_NAME = 'Changelog Sidecar'
# Point directly to the resources root for icons
SHOW_EDIT_RESOURCE_FOLDER = get_resource_folder()
SHOW_EDIT_COMMAND_TOOLTIP = 'Opens the Changelog Sidecar command dialog.'
SHOW_EDIT_TOOLCLIP_FILENAME = 'resources/AppIconHorizontal.png'

