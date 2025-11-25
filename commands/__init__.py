"""
Bootstrapper for the 'commands' package.
"""
# NEW IMPORT: We only need the one Palette command now
from . import PaletteCommand

# List to keep track of all commands
_commands = [
    PaletteCommand
]

def start():
    """
    Called when the add-in is started.
    This function is responsible for registering all commands.
    """
    # Call the 'start' function on all registered commands
    for command in _commands:
        command.start()

def stop():
    """
    Called when the add-in is stopped.
    This function is responsible for un-registering all commands.
    """
    # Call the 'stop' function on all registered commands
    for command in _commands:
        command.stop()