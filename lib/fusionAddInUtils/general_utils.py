"""
General-purpose utility functions for the add-in.

Currently contains the main 'handle_error' function, which
provides a standardized, user-friendly error dialog
with a full traceback for debugging.
"""
import traceback
import adsk.core


def handle_error(name: str):
    """
    Prints a stack trace when an error occurs.
    """
    ui = adsk.core.Application.get().userInterface
    if ui:
        ui.messageBox(f'Error in {name}:\n{traceback.format_exc()}')
        