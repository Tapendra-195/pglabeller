import tkinter as tk
from tkinter import ttk

class WidgetManager:
    def __init__(self, master):
        self.master = master
        self.widgets = {}  # Dictionary to store widget references

    def add_widget(self, name, widget_class, pack=True, **kwargs):
        # Pop 'layout_options' from kwargs if provided so it doesn't get passed to the widget
        layout_options = kwargs.pop("layout_options", None)
        widget = widget_class(self.master, **kwargs)
        self.widgets[name] = widget
        if pack:
            if layout_options:
                widget.pack(**layout_options)
            else:
                widget.pack(pady=5)
        return widget

    def get_widget(self, name):
        """Return the widget registered with the given name."""
        return self.widgets.get(name)

    def enable_widget(self, name):
        """Enable a widget by name."""
        widget = self.get_widget(name)
        if widget:
            if isinstance(widget, ttk.Widget):  # For ttk widgets
                widget.state(["!disabled"])  # Remove 'disabled' state
            elif "state" in widget.config():  # Check if 'state' is a valid option
                widget.config(state="normal")  # Enable standard Tkinter widgets

    def disable_widget(self, name):
        """Disable a widget by name."""
        widget = self.get_widget(name)
        if widget:
            if hasattr(widget, "state"):
                widget.state(["disabled"])
            elif "state" in widget.config():
                widget.config(state="disabled")

    '''
                
    def disable_widget(self, name):
        """Disable a widget by name."""
        widget = self.get_widget(name)
        if widget:
            if isinstance(widget, ttk.Widget):  # For ttk widgets
                widget.state(["disabled"])
            elif "state" in widget.config():  # Check if 'state' is a valid option
                widget.config(state="disabled")
                
    

    
    def enable_widget(self, name):
        """Enable a widget by name."""
        widget = self.get_widget(name)
        if widget:
            if hasattr(widget, "state"):
                widget.state(['!disabled'])
            else:
                widget.config(state="normal")

    def disable_widget(self, name):
        """Disable a widget by name."""
        widget = self.get_widget(name)
        if widget:
            if hasattr(widget, "state"):
                widget.state(['disabled'])
            else:
                widget.config(state="disabled")
    
    def attach_command(self, name, command):
        """
        Attach a command to a widget that supports the 'command' option.
        """
        widget = self.get_widget(name)
        if widget:
            try:
                widget.config(command=command)
            except tk.TclError:
                print(f"Widget '{name}' does not support commands.")
    '''
