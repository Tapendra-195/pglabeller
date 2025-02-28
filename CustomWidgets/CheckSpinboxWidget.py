import tkinter as tk
from tkinter import ttk

class CheckSpinboxWidget(ttk.Frame):
    def __init__(self, master, label_text="Enable Value:", default_values=(False, "20"),
                 min_value=0, max_value=100, **kwargs):
        super().__init__(master, **kwargs)
        
        # Store min and max values for validation.
        self.min_value = min_value
        self.max_value = max_value
        
        # Create custom styles for the spinbox.
        self.style = ttk.Style()
        self.style.configure("Normal.TSpinbox", fieldbackground="white")
        self.style.configure("Red.TSpinbox", fieldbackground="#ff9999")
        
        # Create variables for the checkbutton and spinbox.
        self.var_check = tk.BooleanVar(value=default_values[0])
        self.var_spin = tk.StringVar(value=str(default_values[1]))
        
        # Create a checkbutton.
        self.check = ttk.Checkbutton(self, text=label_text, variable=self.var_check,
                                     command=self.toggle_spinbox)
        # Create a ttk.Spinbox with validation.
        self.spin = ttk.Spinbox(
            self, from_=min_value, to=max_value, textvariable=self.var_spin,
            width=8, validate="focusout",
            validatecommand=(self.register(self.validate_entry), "%P"),
            style="Normal.TSpinbox"
        )
        
        # Layout: checkbox on the left and spinbox on the right.
        self.check.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.spin.grid(row=0, column=1, padx=5, pady=5)
        
        # Bind changes to update style based on the spinbox value.
        self.var_spin.trace_add("write", lambda *args: self.check_value())
        
        # Set the initial state of the spinbox.
        self.toggle_spinbox()

    def toggle_spinbox(self):
        """Enable or disable the spinbox based on the checkbutton state."""
        if self.var_check.get():
            self.spin.config(state="normal")
        else:
            self.spin.config(state="disabled")
    
    def validate_entry(self, value):
        """Ensure the spinbox input is numeric and within the allowed range."""
        if value.strip() == "":
            return True
        try:
            num = float(value)
            if self.min_value <= num <= self.max_value:
                return True
            else:
                self.after(100, self.reset_entry)
                return False
        except ValueError:
            self.after(100, self.reset_entry)
            return False

    def reset_entry(self):
        """Reset the spinbox value to the minimum value if validation fails."""
        self.var_spin.set(str(self.min_value))
    
    def check_value(self):
        """Optionally update the spinbox style if the value is invalid."""
        try:
            num = float(self.var_spin.get()) if self.var_spin.get().strip() else None
            self.spin.configure(style="Normal.TSpinbox")
            if num is not None and not (self.min_value <= num <= self.max_value):
                self.spin.configure(style="Red.TSpinbox")
        except ValueError:
            pass

    def get_values(self):
        """Return the state of the checkbox and the current spinbox value."""
        return self.var_check.get(), self.var_spin.get()

    def set_values(self, checked, value):
        """Set the checkbox and spinbox values and update the widget state."""
        self.var_check.set(checked)
        self.var_spin.set(value)
        self.toggle_spinbox()
        self.check_value()

    # --- State Management Methods ---
    def set_state(self, state):
        """Enable or disable both the checkbutton and spinbox."""
        if state == "disabled":
            self.check.config(state="disabled")
            self.spin.config(state="disabled")
        elif state == "normal":
            self.check.config(state="normal")
            self.toggle_spinbox()

    def state(self, state_list=None):
        """Mimic widget state behavior."""
        if state_list is None:
            return
        if "disabled" in state_list:
            self.set_state("disabled")
        elif "!disabled" in state_list:
            self.set_state("normal")

    def config(self, **kwargs):
        """Support state changes via config(state=...)."""
        if "state" in kwargs:
            self.set_state(kwargs.pop("state"))
        if kwargs:
            super().config(**kwargs)

# Example Usage:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("CheckBox and Spinbox Widget Example")

    widget = CheckSpinboxWidget(root, label_text="Enable Value:", default_values=(False, "20"),
                                min_value=10, max_value=100)
    widget.pack(padx=10, pady=10)

    def print_values():
        print("Widget values:", widget.get_values())

    btn = ttk.Button(root, text="Get Values", command=print_values)
    btn.pack(pady=10)

    root.mainloop()
