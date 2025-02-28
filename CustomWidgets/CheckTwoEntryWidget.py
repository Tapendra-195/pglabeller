import tkinter as tk
from tkinter import ttk

class CheckTwoEntryWidget(ttk.Frame):
    def __init__(self, master, label_text="Option", default_values=(False, "0", "0"), 
                 min_value=0, max_value=100, **kwargs):
        super().__init__(master, **kwargs)

        # Store min/max values for validation
        self.min_value = min_value
        self.max_value = max_value

        # Ensure correct types
        check_value = bool(default_values[0])  
        entry1_value = str(default_values[1])  
        entry2_value = str(default_values[2])  

        # Create ttk Styles for Entry Color Change
        self.style = ttk.Style()
        self.style.configure("Normal.TEntry", fieldbackground="white")  # Default white
        self.style.configure("Red.TEntry", fieldbackground="#ff9999")  # Light red

        # Create variables
        self.var_check = tk.BooleanVar(value=check_value)
        self.var_entry1 = tk.StringVar(value=entry1_value)
        self.var_entry2 = tk.StringVar(value=entry2_value)

        # Create widgets
        self.check = ttk.Checkbutton(self, text=label_text, variable=self.var_check, command=self.toggle_entries)
        self.entry1 = ttk.Entry(self, textvariable=self.var_entry1, width=8, style="Normal.TEntry", validate="focusout", 
                                validatecommand=(self.register(self.validate_entry), "%P", "1"))
        self.entry2 = ttk.Entry(self, textvariable=self.var_entry2, width=8, style="Normal.TEntry", validate="focusout", 
                                validatecommand=(self.register(self.validate_entry), "%P", "2"))

        # Layout using grid
        self.check.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry1.grid(row=0, column=1, padx=5, pady=5)
        self.entry2.grid(row=0, column=2, padx=5, pady=5)

        # Bind events for real-time validation and color change
        self.var_entry1.trace_add("write", lambda *args: self.check_values("1"))
        self.var_entry2.trace_add("write", lambda *args: self.check_values("2"))

        # Initially enable/disable based on checkbox state
        self.toggle_entries()

    def toggle_entries(self):
        """Enable or disable entry fields based on checkbox state."""
        state = "normal" if self.var_check.get() else "disabled"
        self.entry1.config(state=state)
        self.entry2.config(state=state)

    def validate_entry(self, value, entry_id):
        """Ensure entry value stays within the specified range."""
        if value.strip() == "":  # Allow empty input
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
        """Reset entry to the closest valid value."""
        if entry_id == "1":
            self.var_entry1.set(str(self.min_value))
        elif entry_id == "2":
            self.var_entry2.set(str(self.min_value))

    def check_values(self, modified_entry):
        """Change color based on entry comparisons. Highlights the modified entry."""
        try:
            val1 = float(self.var_entry1.get()) if self.var_entry1.get().strip() else None
            val2 = float(self.var_entry2.get()) if self.var_entry2.get().strip() else None

            # Reset both to default style first
            self.entry1.configure(style="Normal.TEntry")
            self.entry2.configure(style="Normal.TEntry")

            if val1 is not None and val2 is not None:
                if val1 > val2 and modified_entry == "1":
                    self.entry1.configure(style="Red.TEntry")  # Highlight entry1
                elif val2 < val1 and modified_entry == "2":
                    self.entry2.configure(style="Red.TEntry")  # Highlight entry2

        except ValueError:
            pass  # Ignore errors for non-numeric inputs

    def get_values(self):
        """Returns (checked_state, entry1_value, entry2_value)"""
        return self.var_check.get(), self.var_entry1.get(), self.var_entry2.get()

    def set_values(self, checked, entry1, entry2):
        """Sets values for checkbutton and entries"""
        self.var_check.set(checked)
        self.var_entry1.set(entry1)
        self.var_entry2.set(entry2)
        self.toggle_entries()
        self.check_values("1")  # Update colors for initial values

    # --- New methods to support widget manager enable/disable ---

    def set_state(self, state):
        """Set the overall state of the widget.
        If disabled, disable the checkbutton and both entry widgets.
        If normal, enable the checkbutton and let toggle_entries control the entries."""
        if state == "disabled":
            self.check.config(state="disabled")
            self.entry1.config(state="disabled")
            self.entry2.config(state="disabled")
        elif state == "normal":
            self.check.config(state="normal")
            self.toggle_entries()  # Re-enable entries according to the checkbutton

    def state(self, state_list=None):
        """Mimic widget state behavior.
        When called with state_list containing 'disabled', the widget is disabled.
        When called with state_list containing '!disabled', the widget is enabled."""
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

# Example Usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("CheckEntryRow Example")

    row1 = CheckEntryWidget(root, label_text="Row 1", default_values=(True, "20", "50"), min_value=10, max_value=100)
    row1.pack(pady=5, padx=10, fill="x")

    row2 = CheckEntryWidget(root, label_text="Row 2", default_values=(False, "30", "80"), min_value=5, max_value=200)
    row2.pack(pady=5, padx=10, fill="x")

    def print_values():
        print("Row 1:", row1.get_values())
        print("Row 2:", row2.get_values())

    # Example buttons to disable and enable row1 using the new API
    btn_disable = ttk.Button(root, text="Disable Row 1", command=lambda: row1.state(["disabled"]))
    btn_disable.pack(pady=5)
    btn_enable = ttk.Button(root, text="Enable Row 1", command=lambda: row1.state(["!disabled"]))
    btn_enable.pack(pady=5)

    btn = ttk.Button(root, text="Get Values", command=print_values)
    btn.pack(pady=10)

    root.mainloop()

