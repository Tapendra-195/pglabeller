import tkinter as tk
from tkinter import ttk

class LabelSpinboxWidget(ttk.Frame):
    def __init__(self, master, label_text="Label", default_value="0",
                 min_value=0, max_value=100, **kwargs):
        super().__init__(master, **kwargs)
        
        # Store the min and max values.
        self.min_value = min_value
        self.max_value = max_value
        
        # Create custom styles for the spinbox.
        self.style = ttk.Style()
        self.style.configure("Normal.TSpinbox", fieldbackground="white")
        self.style.configure("Red.TSpinbox", fieldbackground="#ff9999")
        
        # Create a StringVar to hold the spinbox value.
        self.var_spin = tk.StringVar(value=str(default_value))
        
        # Create a static label.
        self.label = ttk.Label(self, text=label_text)
        
        # Create a ttk Spinbox with validation on focus out.
        self.spin = ttk.Spinbox(
            self, from_=min_value, to=max_value, textvariable=self.var_spin,
            width=8, validate="focusout",
            validatecommand=(self.register(self.validate_entry), "%P"),
            style="Normal.TSpinbox"
        )
        
        # Layout: label on the left and spinbox on the right.
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.spin.grid(row=0, column=1, padx=5, pady=5)
        
        # Bind variable changes to update style if necessary.
        self.var_spin.trace_add("write", lambda *args: self.check_value())
    
    def validate_entry(self, value):
        """Ensure the spinbox value is numeric and within the allowed range."""
        if value.strip() == "":
            return True
        try:
            num = float(value)
            if self.min_value <= num <= self.max_value:
                return True
            else:
                # Reset if the value is out of range.
                self.after(100, self.reset_entry)
                return False
        except ValueError:
            self.after(100, self.reset_entry)
            return False

    def reset_entry(self):
        """Reset the spinbox value to the minimum value."""
        self.var_spin.set(str(self.min_value))
    
    def check_value(self):
        """Optionally adjust the spinbox style based on the current value."""
        try:
            num = float(self.var_spin.get()) if self.var_spin.get().strip() else None
            # Reset to normal style.
            self.spin.configure(style="Normal.TSpinbox")
            # Highlight in red if the value is out of bounds.
            if num is not None and not (self.min_value <= num <= self.max_value):
                self.spin.configure(style="Red.TSpinbox")
        except ValueError:
            pass
    
    def get_value(self):
        """Return the current value of the spinbox."""
        return self.var_spin.get()
    
    def set_value(self, value):
        """Set a new value for the spinbox and update the style."""
        self.var_spin.set(str(value))
        self.check_value()
    
    # --- State Management Methods ---
    def set_state(self, state):
        """Enable or disable the spinbox."""
        self.spin.config(state=state)
        
    def state(self, state_list=None):
        if state_list is None:
            return
        if "disabled" in state_list:
            self.set_state("disabled")
        elif "!disabled" in state_list:
            self.set_state("normal")
    
    def config(self, **kwargs):
        """Support setting state via config(state=...)."""
        if "state" in kwargs:
            self.set_state(kwargs.pop("state"))
        if kwargs:
            super().config(**kwargs)

# Example Usage:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Label and Single ttk Spinbox Widget Example")
    
    widget = LabelSpinboxWidget(root, label_text="Enter value:",
                                default_value="20", min_value=10, max_value=100)
    widget.pack(padx=10, pady=10)
    
    def print_value():
        print("Spinbox value:", widget.get_value())
    
    btn = ttk.Button(root, text="Get Value", command=print_value)
    btn.pack(pady=10)
    
    root.mainloop()
