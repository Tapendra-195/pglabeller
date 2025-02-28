import tkinter as tk
from tkinter import ttk

class LabelTwoSpinboxWidget(ttk.Frame):
    def __init__(self, master, label_text="Label", default_values=("0", "0"),
                 min_value=0, max_value=100, **kwargs):
        super().__init__(master, **kwargs)
        
        # Store min and max values for validation.
        self.min_value = min_value
        self.max_value = max_value
        
        # Convert default values to strings.
        spin1_value = str(default_values[0])
        spin2_value = str(default_values[1])
        
        # Create ttk Styles for Spinbox Color Change.
        self.style = ttk.Style()
        # Note: The style element for ttk.Spinbox may differ depending on your Tk version.
        self.style.configure("Normal.TSpinbox", fieldbackground="white")
        self.style.configure("Red.TSpinbox", fieldbackground="#ff9999")
        
        # Create StringVar variables for spinboxes.
        self.var_spin1 = tk.StringVar(value=spin1_value)
        self.var_spin2 = tk.StringVar(value=spin2_value)
        
        # Create a static label.
        self.label = ttk.Label(self, text=label_text)
        
        # Create two ttk Spinboxes with validation.
        self.spin1 = ttk.Spinbox(self, from_=min_value, to=max_value, textvariable=self.var_spin1,
                                  width=8, validate="focusout",
                                  validatecommand=(self.register(self.validate_entry), "%P", "1"),
                                  style="Normal.TSpinbox")
        self.spin2 = ttk.Spinbox(self, from_=min_value, to=max_value, textvariable=self.var_spin2,
                                  width=8, validate="focusout",
                                  validatecommand=(self.register(self.validate_entry), "%P", "2"),
                                  style="Normal.TSpinbox")
        
        # Layout: label on the left, then the two spinboxes.
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.spin1.grid(row=0, column=1, padx=5, pady=5)
        self.spin2.grid(row=0, column=2, padx=5, pady=5)
        
        # Bind changes to update the style based on value comparison.
        self.var_spin1.trace_add("write", lambda *args: self.check_values("1"))
        self.var_spin2.trace_add("write", lambda *args: self.check_values("2"))
    
    def validate_entry(self, value, entry_id):
        """Validate that the input is numeric and within the allowed range.
           If invalid, the spinbox is reset shortly after."""
        if value.strip() == "":
            return True
        try:
            num = float(value)
            if self.min_value <= num <= self.max_value:
                return True
            else:
                self.after(100, lambda: self.reset_entry(entry_id))
                return False
        except ValueError:
            self.after(100, lambda: self.reset_entry(entry_id))
            return False

    def reset_entry(self, entry_id):
        """Reset the spinbox to the minimum value if validation fails."""
        if entry_id == "1":
            self.var_spin1.set(str(self.min_value))
        elif entry_id == "2":
            self.var_spin2.set(str(self.min_value))

    def check_values(self, modified_entry):
        """Highlight the modified spinbox in red if the first value is greater than the second."""
        try:
            val1 = float(self.var_spin1.get()) if self.var_spin1.get().strip() else None
            val2 = float(self.var_spin2.get()) if self.var_spin2.get().strip() else None
            
            # Reset both spinboxes to normal style.
            self.spin1.configure(style="Normal.TSpinbox")
            self.spin2.configure(style="Normal.TSpinbox")
            
            if val1 is not None and val2 is not None:
                if val1 > val2:
                    if modified_entry == "1":
                        self.spin1.configure(style="Red.TSpinbox")
                    elif modified_entry == "2":
                        self.spin2.configure(style="Red.TSpinbox")
        except ValueError:
            pass  # Ignore non-numeric inputs.
    
    def get_values(self):
        """Return the current values of the two spinboxes."""
        return self.var_spin1.get(), self.var_spin2.get()
    
    def set_values(self, val1, val2):
        """Set new values for the spinboxes and update the style accordingly."""
        self.var_spin1.set(val1)
        self.var_spin2.set(val2)
        self.check_values("1")
    
    # --- State Management Methods ---
    def set_state(self, state):
        """Enable or disable both spinboxes."""
        if state == "disabled":
            self.spin1.config(state="disabled")
            self.spin2.config(state="disabled")
        elif state == "normal":
            self.spin1.config(state="normal")
            self.spin2.config(state="normal")
    
    def state(self, state_list=None):
        """Mimic widget state behavior."""
        if state_list is None:
            return
        if "disabled" in state_list:
            self.set_state("disabled")
        elif "!disabled" in state_list:
            self.set_state("normal")
    
    def config(self, **kwargs):
        """Override config to support state changes via config(state=...)."""
        if "state" in kwargs:
            self.set_state(kwargs.pop("state"))
        if kwargs:
            super().config(**kwargs)

# Example Usage:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Label and Two ttk Spinbox Widget Example")
    
    widget = LabelTwoSpinboxWidget(root, label_text="Enter range:",
                                   default_values=("20", "50"), min_value=10, max_value=100)
    widget.pack(padx=10, pady=10)
    
    def print_values():
        print("Spinbox values:", widget.get_values())
    
    btn = ttk.Button(root, text="Get Values", command=print_values)
    btn.pack(pady=10)
    
    root.mainloop()
