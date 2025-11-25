"""
Utility functions for managing Fusion 360 API event handlers.

Provides a robust way to add and clear event handlers,
tracking them in a global list to ensure all handlers
are properly removed when the add-in stops.
"""
import adsk.core
from .general_utils import handle_error

# Contains a list of all the event handlers that are currently active.
_handlers = []


def add_handler(event: adsk.core.Event, handler_class: callable):
    """
    Adds a handler to the specified event and tracks it.
    """
    global _handlers
    try:
        # ***** THIS IS THE FIX *****
        # We must create an INSTANCE of the handler class
        handler_instance = handler_class()
        
        # Then add the INSTANCE to the event
        event.add(handler_instance)
        
        # And store the INSTANCE so we can remove it later
        _handlers.append({'event': event, 'handler': handler_instance})
        
    except:
        handle_error('add_handler')


def clear_handlers():
    """
    Clears all active event handlers.
    """
    global _handlers
    try:
        for item in _handlers:
            item['event'].remove(item['handler'])
        _handlers = []
    except:
        handle_error('clear_handlers')