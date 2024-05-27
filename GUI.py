import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from PIL import Image, ImageDraw
import source_configuration as sc
import pandas as pd

# Placeholder function for the image generation
def get_placeholder_image():
    from PIL import Image, ImageDraw
    image = Image.new('RGB', (600, 600), 'black')
    draw = ImageDraw.Draw(image)
    draw.text((150, 300), "Utopian Automated Laboratory", fill="white")
    image.save("placeholder_image.png")
    return "placeholder_image.png"

class BerthaGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("BERTHA self-driving laboratory")
        self.geometry("600x600")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle window close
        self.config_file = "config.json"
        self.load_config()

        self.create_widgets()
        self.apply_dark_theme()

    def create_widgets(self):
        self.placeholder_image = tk.PhotoImage(file=get_placeholder_image())
        self.background_label = tk.Label(self, image=self.placeholder_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.title_label = tk.Label(self, text="BERTHA self-driving laboratory", font=("Helvetica", 16), bg="black", fg="white")
        self.title_label.pack(pady=20)

        self.enter_workflow_button = tk.Button(self, text="Enter self-driving workflow…", command=self.enter_workflow)
        self.enter_workflow_button.pack(pady=10)

        self.run_recipe_button = tk.Button(self, text="Run standard recipe…", command=self.run_standard_recipe)
        self.run_recipe_button.pack(pady=10)

        self.system_setup_button = tk.Button(self, text="System setup", command=self.system_setup)
        self.system_setup_button.pack(pady=10)

    def apply_dark_theme(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", background="gray20", foreground="white", borderwidth=1)
        style.map("TButton", background=[('active', 'gray30')])
        self.configure(background='black')

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                self.config_data = json.load(file)
        else:
            self.config_data = {}

    def save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.config_data, file)

    def enter_workflow(self):
        self.withdraw()
        WorkflowWindow(self)

    def run_standard_recipe(self):
        self.withdraw()
        RecipeWindow(self)

    def system_setup(self):
        self.withdraw()
        SetupWindow(self)

    def on_closing(self):
        self.destroy()
        self.quit()
        
class SetupWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("System Setup")
        self.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        self.frame = ttk.Frame(self)
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        self.source_setup_label = ttk.Label(self.frame, text="Source Setup")
        self.source_setup_label.grid(row=0, column=0, columnspan=7)

        self.headers = ["Source 1", "Source 2", "Source 3", "Source 4", "Source 5", "Source 6"]
        self.list_names = ["materials", "supplies", "targets", "max_powers"]

        for col, header in enumerate(self.headers, 1):
            ttk.Label(self.frame, text=header).grid(row=1, column=col)

        self.entries = {}
        for row, list_name in enumerate(self.list_names, 2):
            ttk.Label(self.frame, text=list_name).grid(row=row, column=0, sticky=tk.E)
            self.entries[list_name] = []
            for col, value in enumerate(getattr(sc, list_name), 1):
                entry = ttk.Entry(self.frame)
                entry.grid(row=row, column=col)
                entry.insert(0, str(value))  # Populate with initial values from `sc`
                entry.configure(state='readonly')
                self.entries[list_name].append(entry)

        self.edit_button = ttk.Button(self.frame, text="Edit", command=self.edit_entries)
        self.edit_button.grid(row=len(self.list_names) + 2, column=1, columnspan=3, pady=10)

        self.close_button = ttk.Button(self.frame, text="Close", command=self.on_close)
        self.close_button.grid(row=len(self.list_names) + 2, column=4, columnspan=3, pady=10)

    def edit_entries(self):
        for entry_list in self.entries.values():
            for entry in entry_list:
                entry.configure(state='normal')

    def on_close(self):
        if any(entry.get() != str(getattr(sc, list_name)[col-1]) for list_name, entry_list in self.entries.items() for col, entry in enumerate(entry_list, 1)):
            if messagebox.askyesno("Confirm", "Save changes?"):
                self.update_source_config()
        self.parent.deiconify()
        self.destroy()

    def update_source_config(self):
        for list_name, entry_list in self.entries.items():
            updated_values = [entry.get() for entry in entry_list]
            setattr(sc, list_name, updated_values)

        # Write updated configuration back to source_configuration.py
        sc_dict = {name: getattr(sc, name) for name in self.list_names}
        with open('source_configuration.py', 'w') as f:
            f.write('import ast\n\n')
            for name, values in sc_dict.items():
                f.write(f"{name} = {values}\n")


class RecipeWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Run Standard Recipe")
        self.geometry("800x800")

        self.recipe_dir = r"C:\Users\jonsc690\Documents\BEA-supervisor\Recipes"
        self.create_widgets()

    def create_widgets(self):
        self.process_frame = ttk.Frame(self, width=200)
        self.process_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.recipe_preview_frame = ttk.Frame(self)
        self.recipe_preview_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Process setup widgets
        self.recipe_label = ttk.Label(self.process_frame, text="Recipe")
        self.recipe_label.pack(pady=5)

        self.recipe_combobox = ttk.Combobox(self.process_frame)
        self.recipe_combobox.pack(pady=5)
        self.load_recipes()

        self.presputter_label = ttk.Label(self.process_frame, text="Presputter Time (s)")
        self.presputter_label.pack(pady=5)

        self.presputter_entry = ttk.Entry(self.process_frame)
        self.presputter_entry.pack(pady=5)

        self.qcms_frame = ttk.LabelFrame(self.process_frame, text="QCMs")
        self.qcms_frame.pack(pady=5, fill=tk.X)

        self.use_qcms_toggle = ttk.Checkbutton(self.qcms_frame, text="Use QCMs")
        self.use_qcms_toggle.pack(side=tk.LEFT, padx=5, pady=5)

        self.min_qcm_toggle = ttk.Checkbutton(self.qcms_frame, text="Minimize QCM Exposure")
        self.min_qcm_toggle.pack(side=tk.LEFT, padx=5, pady=5)

        self.iterations_label = ttk.Label(self.process_frame, text="Iterations")
        self.iterations_label.pack(pady=5)

        self.iterations_entry = ttk.Entry(self.process_frame)
        self.iterations_entry.pack(pady=5)

        self.make_samples_check = ttk.Checkbutton(self.process_frame, text="Make Samples")
        self.make_samples_check.pack(pady=5)

        # Recipe preview widgets
        self.recipe_preview_label = ttk.Label(self.recipe_preview_frame, text="Recipe Preview")
        self.recipe_preview_label.pack(pady=5)

        self.recipe_preview_text = tk.Text(self.recipe_preview_frame)
        self.recipe_preview_text.pack(expand=True, fill=tk.BOTH, pady=5)

        self.sim_save_frame = ttk.Frame(self)
        self.sim_save_frame.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=10)

        self.simulate_toggle = ttk.Checkbutton(self.sim_save_frame, text="Simulate")
        self.simulate_toggle.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_toggle = ttk.Checkbutton(self.sim_save_frame, text="Save")
        self.save_toggle.pack(side=tk.LEFT, padx=5, pady=5)

        self.run_cancel_frame = ttk.Frame(self)
        self.run_cancel_frame.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=10)

        self.run_button = ttk.Button(self.run_cancel_frame, text="Run Recipe", command=self.run_recipe)
        self.run_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.cancel_button = ttk.Button(self.run_cancel_frame, text="Cancel", command=self.on_close)
        self.cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

    def load_recipes(self):
        recipe_files = [f for f in os.listdir(self.recipe_dir) if f.endswith('.txt')]
        self.recipe_combobox['values'] = recipe_files
        self.recipe_combobox.bind('<<ComboboxSelected>>', self.display_recipe)

    def display_recipe(self, event):
        selected_recipe = self.recipe_combobox.get()
        recipe_path = os.path.join(self.recipe_dir, selected_recipe)
        if os.path.isfile(recipe_path):
            with open(recipe_path, 'r') as file:
                recipe_content = file.read()
            self.recipe_preview_text.delete('1.0', tk.END)
            self.recipe_preview_text.insert(tk.END, recipe_content)

    def run_recipe(self):
        # Logic to run the recipe
        pass

    def on_close(self):
        self.parent.deiconify()
        self.destroy()


class WorkflowWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Enter Self-Driving Workflow")
        self.geometry("800x1000")

        self.create_widgets()

    def create_widgets(self):
        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.load_button = ttk.Button(self.top_frame, text="Load Workflow…")
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.new_button = ttk.Button(self.top_frame, text="New Workflow…")
        self.new_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_run_close_frame = ttk.Frame(self)
        self.save_run_close_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.save_button = ttk.Button(self.save_run_close_frame, text="Save Workflow")
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.run_button = ttk.Button(self.save_run_close_frame, text="Run Experiments")
        self.run_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.close_button = ttk.Button(self.save_run_close_frame, text="Close", command=self.on_close)
        self.close_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.tab_control = ttk.Notebook(self)
        self.tab_control.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.workflow_stages = ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage 5"]

        for stage in self.workflow_stages:
            tab = ttk.Frame(self.tab_control)
            self.tab_control.add(tab, text=stage)

            if stage == "Stage 1":
                self.create_stage_1_widgets(tab)

    def create_stage_1_widgets(self, tab):
        self.table_label = ttk.Label(tab, text="Targeted Material Compositions")
        self.table_label.pack(pady=5)

        self.table_frame = ttk.Frame(tab)
        self.table_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.table_headers = ["Material 1", "Material 2", "Material 3", "Material 4", "Material 5", "Material 6"]
        self.table_entries = {}

        for col, header in enumerate(self.table_headers):
            ttk.Label(self.table_frame, text=header).grid(row=0, column=col + 1)
        
        for row in range(1, 9):
            ttk.Label(self.table_frame, text=str(row)).grid(row=row, column=0)
            self.table_entries[row] = []
            for col in range(1, 7):
                entry = ttk.Entry(self.table_frame)
                entry.grid(row=row, column=col)
                self.table_entries[row].append(entry)

        for row in range(1, 9):
            ttk.Button(self.table_frame, text="Fix Target", command=lambda r=row: self.fix_target(r)).grid(row=row, column=7)

    def fix_target(self, row):
        # Here you would implement the logic for fixing the target
        pass

    def on_close(self):
        self.parent.deiconify()
        self.destroy()

if __name__ == "__main__":
    app = BerthaGUI()
    app.mainloop()
