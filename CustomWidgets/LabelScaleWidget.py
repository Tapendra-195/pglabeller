import tkinter as tk
from tkinter import ttk

class LabelScaleWidget(ttk.Frame):
    def __init__(self, master, label_text="Label", min_value=0, max_value=100, 
                 default_value=None, orient="horizontal", **kwargs):
        # Extract the command callback from kwargs, if provided.
        self._command = kwargs.pop("command", None)
        super().__init__(master, **kwargs)
        
        self.min_value = min_value
        self.max_value = max_value
        # Use the default value if provided; otherwise, default to min_value.
        if default_value is None:
            default_value = min_value

        # Variable to hold the scale's value.
        self.value_var = tk.DoubleVar(value=default_value)
        
        # Create the label.
        self.label = ttk.Label(self, text=label_text)
        # Create the scale widget with the command set to a wrapper method.
        self.scale = ttk.Scale(
            self, orient=orient, from_=min_value, to=max_value,
            variable=self.value_var, command=self._on_scale_change
        )
        
        # Layout: label on the left, scale on the right.
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.scale.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.columnconfigure(1, weight=1)

    def _on_scale_change(self, value):
        """Internal method called whenever the scale's value changes.
        Calls the provided command with the new value if one was passed in kwargs."""
        if self._command:
            self._command(value)

    def get_value(self):
        """Return the current value of the scale."""
        return self.value_var.get()

    def set_value(self, value):
        """Set a new value for the scale."""
        self.value_var.set(value)

    def state(self, states=None):
        """Get or set the state of the entry widget.
        
        When called with no arguments, returns the current state.
        When provided with a list of states, sets the entry state:
        - If 'disabled' is in the list, disable the entry.
        - Otherwise, enable it.
        """
        if states is None:
            return self.scale.cget("state")
        else:
            if "disabled" in states:
                self.scale.config(state="disabled")
            else:
                self.scale.config(state="normal")

        
# Example Usage:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Label and Scale Widget with Command in kwargs Example")
    
    def scale_changed(new_value):
        print("Scale changed to:", new_value)
    
    # Pass the command callback in the kwargs.
    widget = LabelScaleWidget(root, label_text="Volume:", min_value=0, max_value=100, 
                              default_value=50, command=scale_changed)
    widget.pack(padx=10, pady=10, fill="x")
    
    btn = ttk.Button(root, text="Get Value", command=lambda: print("Current value:", widget.get_value()))
    btn.pack(pady=10)
    
    root.mainloop()

'''

import tkinter as tk
from tkinter import ttk

class LabelScaleWidget(ttk.Frame):
    def __init__(self, master, label_text="Label", min_value=0, max_value=100, default_value=None, orient="horizontal", **kwargs):
        super().__init__(master, **kwargs)
        
        self.min_value = min_value
        self.max_value = max_value
        # Use the default value if provided, otherwise set to min_value.
        if default_value is None:
            default_value = min_value

        # Variable to hold the scale's value.
        self.value_var = tk.DoubleVar(value=default_value)
        
        # Create the label.
        self.label = ttk.Label(self, text=label_text)
        # Create the scale widget. Note that ttk.Scale uses the 'from_' and 'to' options.
        self.scale = ttk.Scale(self, orient=orient, from_=min_value, to=max_value, variable=self.value_var)
        
        # Layout: label on the left, scale on the right.
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.scale.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Allow the scale column to expand.
        self.columnconfigure(1, weight=1)

    def get_value(self):
        """Return the current value of the scale."""
        return self.value_var.get()

    def set_value(self, value):
        """Set a new value for the scale."""
        self.value_var.set(value)

# Example Usage:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Label and Scale Widget Example")
    
    # Create a widget with a label and a scale that goes from 0 to 100 with a default value of 50.
    widget = LabelScaleWidget(root, label_text="Volume:", min_value=0, max_value=100, default_value=50)
    widget.pack(padx=10, pady=10, fill="x")
    
    def print_value():
        print("Scale value:", widget.get_value())
    
    btn = ttk.Button(root, text="Get Value", command=print_value)
    btn.pack(pady=10)
    
    root.mainloop()
'''
