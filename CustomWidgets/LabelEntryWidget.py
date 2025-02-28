import tkinter as tk
from tkinter import ttk

class LabelEntryWidget(ttk.Frame):
    def __init__(self, master, label_text="Label", default_value="0", min_value=0, **kwargs):
        super().__init__(master, **kwargs)
        
        # Store the minimum value.
        self.min_value = min_value
        
        # Create custom styles for the entry.
        self.style = ttk.Style()
        self.style.configure("Normal.TEntry", fieldbackground="white")
        self.style.configure("Red.TEntry", fieldbackground="#ff9999")
        
        # Create a StringVar to hold the entry value.
        self.var_entry = tk.StringVar(value=str(default_value))
        
        # Create a static label.
        self.label = ttk.Label(self, text=label_text)
        
        # Create an entry widget with validation on focus out.
        self.entry = ttk.Entry(
            self, textvariable=self.var_entry, width=10,
            style="Normal.TEntry", validate="focusout",
            validatecommand=(self.register(self.validate_entry), "%P")
        )
        
        # Layout: label on the left, then entry.
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Bind variable changes to update the style.
        self.var_entry.trace_add("write", lambda *args: self.check_value())
    
    def validate_entry(self, value):
        """Validate that the input is numeric and at least the minimum value."""
        if value.strip() == "":
            return True  # Allow empty input if desired.
        try:
            num = float(value)
            if num >= self.min_value:
                return True
            else:
                self.after(100, self.reset_entry)
                return False
        except ValueError:
            self.after(100, self.reset_entry)
            return False
    
    def reset_entry(self):
        """Reset the entry value to the minimum value."""
        self.var_entry.set(str(self.min_value))
    
    def check_value(self):
        """Update the entry style based on whether the value is below the minimum."""
        try:
            num = float(self.var_entry.get()) if self.var_entry.get().strip() else None
            self.entry.configure(style="Normal.TEntry")
            if num is not None and num < self.min_value:
                self.entry.configure(style="Red.TEntry")
        except ValueError:
            self.entry.configure(style="Red.TEntry")
    
    def get_value(self):
        """Return the current value of the entry."""
        return self.var_entry.get()
    
    def set_value(self, value):
        """Set a new value for the entry and update its style."""
        self.var_entry.set(str(value))
        self.check_value()
    
    def set_state(self, state):
        """Enable or disable the entry."""
        self.entry.config(state=state)
        
    def config(self, **kwargs):
        """Support setting state via config(state=...)."""
        if "state" in kwargs:
            self.set_state(kwargs.pop("state"))
        if kwargs:
            super().config(**kwargs)

    def state(self, states=None):
        """Get or set the state of the entry widget.
        
        When called with no arguments, returns the current state.
        When provided with a list of states, sets the entry state:
        - If 'disabled' is in the list, disable the entry.
        - Otherwise, enable it.
        """
        if states is None:
            return self.entry.cget("state")
        else:
            if "disabled" in states:
                self.entry.config(state="disabled")
            else:
                self.entry.config(state="normal")
            
# Example Usage:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Label and Entry Widget with Minimum Value")
    
    # Create widget with a label and an entry that requires a value >= 10.
    widget = LabelEntryWidget(root, label_text="Enter value:", default_value="5", min_value=10)
    widget.pack(padx=10, pady=10)
    
    def print_value():
        print("Entry value:", widget.get_value())
        
    btn = ttk.Button(root, text="Get Value", command=print_value)
    btn.pack(pady=10)
    
    root.mainloop()
