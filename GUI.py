import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from PIL import Image, ImageDraw
import source_configuration as sc
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Placeholder function for the image generation
def get_placeholder_image():
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

        self.use_qcms_toggle_var = tk.IntVar(value=0)  # Default unchecked
        self.use_qcms_toggle = ttk.Checkbutton(self.qcms_frame, text="Use QCMs", variable=self.use_qcms_toggle_var)
        self.use_qcms_toggle.pack(side=tk.LEFT, padx=5, pady=5)

        self.min_qcm_toggle_var = tk.IntVar(value=0)  # Default unchecked
        self.min_qcm_toggle = ttk.Checkbutton(self.qcms_frame, text="Minimize QCM Exposure", variable=self.min_qcm_toggle_var)
        self.min_qcm_toggle.pack(side=tk.LEFT, padx=5, pady=5)

        self.iterations_label = ttk.Label(self.process_frame, text="Iterations")
        self.iterations_label.pack(pady=5)

        self.iterations_entry = ttk.Entry(self.process_frame)
        self.iterations_entry.pack(pady=5)

        self.make_samples_check_var = tk.IntVar(value=0)  # Default unchecked
        self.make_samples_check = ttk.Checkbutton(self.process_frame, text="Make Samples", variable=self.make_samples_check_var)
        self.make_samples_check.pack(pady=5)

        # Recipe preview widgets
        self.recipe_preview_label = ttk.Label(self.recipe_preview_frame, text="Recipe Preview")
        self.recipe_preview_label.pack(pady=5)

        self.recipe_preview_text = tk.Text(self.recipe_preview_frame)
        self.recipe_preview_text.pack(expand=True, fill=tk.BOTH, pady=5)

        self.sim_save_frame = ttk.Frame(self)
        self.sim_save_frame.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=10)

        self.simulate_toggle_var = tk.IntVar(value=0)  # Default unchecked
        self.simulate_toggle = ttk.Checkbutton(self.sim_save_frame, text="Simulate", variable=self.simulate_toggle_var)
        self.simulate_toggle.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_toggle_var = tk.IntVar(value=0)  # Default unchecked
        self.save_toggle = ttk.Checkbutton(self.sim_save_frame, text="Save", variable=self.save_toggle_var)
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
        self.protocol("WM_DELETE_WINDOW", self.on_close)  # Handle window close event

        self.workflow_dir = "workflow definition files"
        os.makedirs(self.workflow_dir, exist_ok=True)

        self.active_sources = [False] * 6  # Initialize active_sources as a class variable
        self.loaded_workflow_file = tk.StringVar(value="No file loaded")  # Variable to hold the name of the loaded workflow file
        self.target_compositions_df = pd.DataFrame()  # Initialize the dataframe
        self.current_workflow_file = None  # Store the current workflow file path
        self.workflow_data = {}  # Store workflow data
        self.create_widgets()

    def create_widgets(self):
        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.load_button = ttk.Button(self.top_frame, text="Load Workflow…", command=self.load_workflow)
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.new_button = ttk.Button(self.top_frame, text="New Workflow…", command=self.new_workflow)
        self.new_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.loaded_file_label = ttk.Label(self.top_frame, textvariable=self.loaded_workflow_file)
        self.loaded_file_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_run_close_frame = ttk.Frame(self)
        self.save_run_close_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.save_button = ttk.Button(self.save_run_close_frame, text="Save Workflow", command=self.save_workflow)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.run_button = ttk.Button(self.save_run_close_frame, text="Run Experiments")
        self.run_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.close_button = ttk.Button(self.save_run_close_frame, text="Close", command=self.on_close)
        self.close_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.tab_control = ttk.Notebook(self)
        self.tab_control.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.workflow_stages = ["Define Target Compositions", "Find Boundaries", "Learn Sputter Process", "Calibrate Compositions", "Learn Feature Map", "Feature Identification"]

        self.tabs = {}  # Store tabs to enable/disable them later

        for stage in self.workflow_stages:
            tab = ttk.Frame(self.tab_control)
            self.tab_control.add(tab, text=stage)
            self.tabs[stage] = tab

            if stage == "Define Target Compositions":
                self.create_stage_1_widgets(tab)
            elif stage == "Find Boundaries":
                self.create_find_boundaries_tab(tab)
            elif stage == "Learn Sputter Process":
                self.create_learn_sputter_process_tab(tab)

        # Disable all tabs except the first one
        for i in range(1, len(self.workflow_stages)):
            self.tab_control.tab(i, state="disabled")

    def create_stage_1_widgets(self, tab):
        self.table_label = ttk.Label(tab, text="Targeted Material Compositions")
        self.table_label.pack(pady=5)

        self.table_frame = ttk.Frame(tab)
        self.table_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.table_headers = []
        self.table_entries = {}

        for row in range(1, 9):
            ttk.Label(self.table_frame, text=str(row)).grid(row=row, column=0)
            self.table_entries[row] = []

    def update_table_headers(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        headers = [sc.materials[i] for i, active in enumerate(self.active_sources) if active]
        headers.append("Bind Target")  # Add the "Bind Target" header

        self.table_headers = headers

        for col, header in enumerate(headers):
            ttk.Label(self.table_frame, text=header).grid(row=0, column=col + 1)

        for row in range(1, 9):
            ttk.Label(self.table_frame, text=str(row)).grid(row=row, column=0)
            self.table_entries[row] = []
            for col in range(len(headers) - 1):  # Adjust for "Bind Target" column
                entry = ttk.Entry(self.table_frame, validate="key", validatecommand=(self.register(self.validate_positive_integer), '%P'))
                entry.insert(0, "0")  # Initialize each entry with 0
                entry.grid(row=row, column=col + 1)
                self.table_entries[row].append(entry)
            bind_button = ttk.Button(self.table_frame, text="Bind Target", command=lambda row=row: self.bind_target(row))
            bind_button.grid(row=row, column=len(headers))
            self.table_entries[row].append(bind_button)  # Add button to entries for disabling later

    def validate_positive_integer(self, value_if_allowed):
        if value_if_allowed.isdigit() or value_if_allowed == "":
            return True
        else:
            return False

    def bind_target(self, row):
        values = [entry.get() for entry in self.table_entries[row] if isinstance(entry, ttk.Entry)]
        non_zero_values = [int(value) for value in values if value.isdigit() and int(value) > 0]

        if len(non_zero_values) < 2:
            messagebox.showwarning("Warning", "Please enter at least two non-zero values in the row.")
            return

        if messagebox.askokcancel("Bind Target", "Bind new target composition to the workflow?"):
            new_row = {header: value for header, value in zip(self.table_headers[:-1], values)}  # Exclude "Bind Target" column
            new_row_df = pd.DataFrame([new_row])
            self.target_compositions_df = pd.concat([self.target_compositions_df, new_row_df], ignore_index=True)
            print(f"Updated target_compositions_df: {self.target_compositions_df}")  # Debug print

            self.save_workflow()  # Save the updated workflow

            for entry in self.table_entries[row]:
                entry.config(state='disabled')  # Disable entries
            self.table_entries[row][-1].config(state='disabled')  # Disable the Bind Target button

            # Enable the next tab if at least one bound target composition exists
            if not self.target_compositions_df.empty:
                self.tab_control.tab(1, state="normal")
            
            # Update FindBoundariesTab immediately
            if hasattr(self, 'find_boundaries_tab'):
                print("Updating dropdown in Find Boundaries tab.")
                self.find_boundaries_tab.update_workflow_data(self.workflow_data)
                self.find_boundaries_tab.populate_dropdown()
                
            # Update LearnSputterProcessTab immediately
            if hasattr(self, 'learn_sputter_process_tab'):
                print("Updating dropdown in Learn Sputter Process tab.")
                self.learn_sputter_process_tab.update_workflow_data(self.workflow_data)
                self.learn_sputter_process_tab.populate_dropdown()

            # Check if any EE_LearnMinimumRate model is bound and enable the "Learn Sputter Process" tab
            if any(key.startswith("EE_LearnMinimumRate_model") for key in self.workflow_data):
                self.tab_control.tab(2, state="normal")

    def load_workflow(self):
        filename = filedialog.askopenfilename(initialdir=self.workflow_dir, filetypes=[("JSON files", "*.json")])
        if filename:
            self.current_workflow_file = filename
            with open(filename, 'r') as file:
                self.workflow_data = json.load(file)
                print(f"Workflow data loaded: {self.workflow_data}")
                self.populate_workflow(self.workflow_data)
                self.loaded_workflow_file.set(f"Loaded: {os.path.basename(filename)}")
                # Enable the second tab if there is at least one bound target composition
                if "target_compositions" in self.workflow_data and self.workflow_data["target_compositions"]:
                    self.target_compositions_df = pd.DataFrame(self.workflow_data["target_compositions"])
                    self.tab_control.tab(1, state="normal")
                    # Restore bound target compositions in the table and disable their fields
                    for row_index, composition in enumerate(self.workflow_data["target_compositions"], start=1):
                        for col_index, (header, value) in enumerate(composition.items()):
                            if header in self.table_headers[:-1]:  # Exclude "Bind Target" column
                                entry = self.table_entries[row_index][self.table_headers.index(header)]
                                entry.delete(0, tk.END)
                                entry.insert(0, value)
                                entry.config(state='disabled')
                        self.table_entries[row_index][-1].config(state='disabled')  # Disable the Bind Target button
                # Update the dropdown in Find Boundaries tab
                if hasattr(self, 'find_boundaries_tab'):
                    print("Updating dropdown in Find Boundaries tab.")
                    self.find_boundaries_tab.update_workflow_data(self.workflow_data)
                # Update the dropdown in Learn Sputter Process tab
                if hasattr(self, 'learn_sputter_process_tab'):
                    print("Updating dropdown in Learn Sputter Process tab.")
                    self.learn_sputter_process_tab.update_workflow_data(self.workflow_data)

                # Enable the Learn Sputter Process tab if there is a bound EE_LearnMinimumRate model
                if any(key.startswith("EE_LearnMinimumRate_model") for key in self.workflow_data):
                    self.tab_control.tab(2, state="normal")

    def save_workflow(self):
        if self.current_workflow_file:
            with open(self.current_workflow_file, 'r') as file:
                data = json.load(file)
            data["target_compositions"] = self.target_compositions_df.to_dict(orient='records')
            with open(self.current_workflow_file, 'w') as file:
                json.dump(data, file)
            self.loaded_workflow_file.set(f"Saved: {os.path.basename(self.current_workflow_file)}")
        else:
            filename = filedialog.asksaveasfilename(initialdir=self.workflow_dir, defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if filename:
                data = self.extract_workflow_data()
                data["target_compositions"] = self.target_compositions_df.to_dict(orient='records')
                with open(filename, 'w') as file:
                    json.dump(data, file)
                self.loaded_workflow_file.set(f"Saved: {os.path.basename(filename)}")
                self.current_workflow_file = filename

        # Enable the Learn Sputter Process tab if there is a bound EE_LearnMinimumRate model
        if any(key.startswith("EE_LearnMinimumRate_model") for key in self.workflow_data):
            self.tab_control.tab(2, state="normal")


    def new_workflow(self):
        # Clear current entries to start a new workflow
        for entry_list in self.table_entries.values():
            for entry in entry_list:
                if isinstance(entry, ttk.Entry):
                    entry.delete(0, tk.END)
                elif isinstance(entry, ttk.Button):
                    entry.config(state='normal')  # Reset button state to normal

        # Reset target compositions DataFrame
        self.target_compositions_df = pd.DataFrame()

        # Create the "choose active sources" popup window
        popup = tk.Toplevel(self)
        popup.title("Choose Active Sources")
        popup.geometry("600x200")

        def toggle_source(index):
            self.active_sources[index] = not self.active_sources[index]

        # Create toggle controls and non-editable fields in the popup
        for i in range(6):
            self.active_sources[i] = False  # Ensure all sources are set to False initially
            toggle_button = ttk.Checkbutton(popup, text=f"Source {i + 1}", command=lambda i=i: toggle_source(i))
            toggle_button.grid(row=0, column=i, padx=10, pady=10)
            value_label = ttk.Label(popup, text=sc.materials[i])
            value_label.grid(row=1, column=i, padx=10, pady=10)

        def create_workflow():
            if sum(self.active_sources) < 2:
                messagebox.showwarning("Warning", "Please choose at least two active sources.")
            else:
                filename = filedialog.asksaveasfilename(initialdir=self.workflow_dir, defaultextension=".json", filetypes=[("JSON files", "*.json")])
                if filename:
                    workflow_data = {
                        "target materials": sc.materials,
                        "active_sources": self.active_sources
                    }
                    with open(filename, 'w') as file:
                        json.dump(workflow_data, file)
                    self.loaded_workflow_file.set(f"Created: {os.path.basename(filename)}")
                    self.update_table_headers()
                    self.current_workflow_file = filename
                    self.workflow_data = workflow_data  # Update workflow_data with the new workflow
                    popup.destroy()

                    # Reset and update FindBoundariesTab
                    if hasattr(self, 'find_boundaries_tab'):
                        self.find_boundaries_tab.reset_state()
                        self.find_boundaries_tab.update_workflow_data(self.workflow_data)

                    # Reset and update LearnSputterProcessTab
                    if hasattr(self, 'learn_sputter_process_tab'):
                        self.learn_sputter_process_tab.reset_state()
                        self.learn_sputter_process_tab.update_workflow_data(self.workflow_data)

        def cancel():
            popup.destroy()

        # Create "Create Workflow" and "Cancel" buttons in the popup
        create_button = ttk.Button(popup, text="Create Workflow", command=create_workflow)
        create_button.grid(row=2, column=2, padx=10, pady=10)

        cancel_button = ttk.Button(popup, text="Cancel", command=cancel)
        cancel_button.grid(row=2, column=3, padx=10, pady=10)

    def extract_workflow_data(self):
        data = {}
        for row, entry_list in self.table_entries.items():
            data[row] = [entry.get() for entry in entry_list if isinstance(entry, ttk.Entry)]
        return data

    def populate_workflow(self, data):
        print(f"Populating workflow with data: {data}")
        self.active_sources = data.get("active_sources", [False] * 6)
        self.update_table_headers()

        if "target_compositions" in data:
            for row_index, composition in enumerate(data["target_compositions"], start=1):
                for col_index, (header, value) in enumerate(composition.items()):
                    if header in self.table_headers[:-1]:  # Exclude "Bind Target" column
                        entry = self.table_entries[row_index][self.table_headers.index(header)]
                        entry.delete(0, tk.END)
                        entry.insert(0, value)
                        entry.config(state='disabled')
                # Disable the Bind Target button for this row
                self.table_entries[row_index][-1].config(state='disabled')

            # Enable the next tab if there is at least one bound target composition
            self.tab_control.tab(1, state="normal")

    def create_find_boundaries_tab(self, tab):
        # Create the "Find Boundaries" tab widgets here
        self.find_boundaries_tab = FindBoundariesTab(tab, self.workflow_data, self)

    def create_learn_sputter_process_tab(self, tab):
        # Create the "Learn Sputter Process" tab widgets here
        self.learn_sputter_process_tab = LearnSputterProcessTab(tab, self.workflow_data, self)

    def on_close(self):
        self.parent.deiconify()
        self.destroy()


class FindBoundariesTab:
    def __init__(self, parent, workflow_data, workflow_window):
        self.parent = parent
        self.workflow_data = workflow_data
        self.workflow_window = workflow_window  # Store the reference to the WorkflowWindow instance
        self.target_materials = []
        self.source_numbers = []
        self.learning_data_dfs = {}  # Initialize a dictionary to store DataFrames for each source_number
        self.create_widgets()
        self.populate_dropdown()

    def create_widgets(self):
        # Main frame for the tab
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Dropdown selection field
        self.selection_label = ttk.Label(self.frame, text="Select Target Material:")
        self.selection_label.pack(pady=5)

        self.selection_var = tk.StringVar()
        self.selection_dropdown = ttk.Combobox(self.frame, textvariable=self.selection_var)
        self.selection_dropdown.pack(pady=5)
        self.selection_dropdown.bind("<<ComboboxSelected>>", self.on_dropdown_selection)

        self.bound_model_label = ttk.Label(self.frame, text="No model bound")
        self.bound_model_label.pack(pady=5)

        # EE_LearnMinimumRate frame
        self.ee_frame = ttk.LabelFrame(self.frame, text="EE_LearnMinimumRate")
        self.ee_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Buttons in the EE_LearnMinimumRate frame
        self.add_training_data_button = ttk.Button(self.ee_frame, text="Add training data", command=self.add_training_data)
        self.add_training_data_button.pack(fill=tk.X, pady=5)

        self.clear_training_data_button = ttk.Button(self.ee_frame, text="Clear training data", command=self.clear_training_data)
        self.clear_training_data_button.pack(fill=tk.X, pady=5)

        self.train_new_model_button = ttk.Button(self.ee_frame, text="Train new model", command=self.open_train_model_popup)
        self.train_new_model_button.pack(fill=tk.X, pady=5)

        self.view_load_models_button = ttk.Button(self.ee_frame, text="View/load models", command=self.open_model_selection_popup)
        self.view_load_models_button.pack(fill=tk.X, pady=5)

        self.bind_current_model_button = ttk.Button(self.ee_frame, text="Bind current model", command=self.bind_current_model, state=tk.DISABLED)
        self.bind_current_model_button.pack(fill=tk.X, pady=5)

        self.re_evaluate_model_button = ttk.Button(self.ee_frame, text="Re-evaluate model", command=self.re_evaluate_model, state=tk.DISABLED)
        self.re_evaluate_model_button.pack(fill=tk.X, pady=5)

        # Training sets field
        self.training_sets_label = ttk.Label(self.ee_frame, text="Training Sets")
        self.training_sets_label.pack(pady=5)
        self.training_sets_listbox = tk.Listbox(self.ee_frame)
        self.training_sets_listbox.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Model viewer frame
        self.model_viewer_frame = ttk.LabelFrame(self.frame, text="Model Viewer")
        self.model_viewer_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.model_viewer_canvas = tk.Canvas(self.model_viewer_frame)
        self.model_viewer_canvas.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Training data frame
        self.training_data_frame = ttk.LabelFrame(self.frame, text="Training Data")
        self.training_data_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.training_data_text = tk.Text(self.training_data_frame, wrap=tk.NONE)
        self.training_data_text.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Add scrollbars to the training data text widget
        self.scroll_x = ttk.Scrollbar(self.training_data_frame, orient=tk.HORIZONTAL, command=self.training_data_text.xview)
        self.scroll_y = ttk.Scrollbar(self.training_data_frame, orient=tk.VERTICAL, command=self.training_data_text.yview)
        self.training_data_text.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    def reset_state(self):
        self.selection_var.set('')
        self.bound_model_label.config(text="No model bound")
        self.training_sets_listbox.delete(0, tk.END)
        self.training_data_text.delete(1.0, tk.END)
        for widget in self.model_viewer_canvas.winfo_children():
            widget.destroy()
        self.bind_current_model_button.config(state=tk.DISABLED)
        self.re_evaluate_model_button.config(state=tk.DISABLED)
        self.learning_data_dfs.clear()  # Clear learning data
        self.populate_dropdown()  # Refresh the dropdown

    def populate_dropdown(self):
        # Extract target materials and source numbers based on active sources
        print(f"Populating dropdown with workflow data: {self.workflow_data}")
        target_materials = self.workflow_data.get("target materials", [])
        active_sources = self.workflow_data.get("active_sources", [])

        self.target_materials = [material for i, material in enumerate(target_materials) if active_sources[i]]
        self.source_numbers = [i + 1 for i, active in enumerate(active_sources) if active]

        print(f"Target materials: {self.target_materials}")
        self.selection_dropdown['values'] = self.target_materials
        self.selection_dropdown.set('')  # Clear the current selection

    def update_workflow_data(self, workflow_data):
        self.workflow_data = workflow_data
        self.populate_dropdown()

    def on_dropdown_selection(self, event):
        selected_material = self.selection_var.get()
        if not selected_material:
            return

        source_number = sc.materials.index(selected_material) + 1
        self.display_training_data(source_number)
        self.update_bound_model_label(selected_material)

        source_key = f"EE_LearnMinimumRate_model_{selected_material}"
        if source_key in self.workflow_data:
            self.re_evaluate_model_button.config(state=tk.NORMAL)
        else:
            self.re_evaluate_model_button.config(state=tk.DISABLED)

        # Clear current model name and deactivate bind button
        self.bound_model_label.config(text="No model bound")
        self.bind_current_model_button.config(state=tk.DISABLED)


    def update_bound_model_label(self, selected_material):
        source_key = f"EE_LearnMinimumRate_model_{selected_material}"
        if source_key in self.workflow_data:
            bound_model = self.workflow_data[source_key]
            self.bound_model_label.config(text=f"Bound model for {selected_material}: {bound_model}")
        else:
            self.bound_model_label.config(text=f"No model bound for {selected_material}")

    def display_training_data(self, source_number):
        if source_number not in self.learning_data_dfs:
            self.learning_data_dfs[source_number] = pd.DataFrame()

        self.training_sets_listbox.delete(0, tk.END)
        self.training_data_text.delete(1.0, tk.END)

        # Add entries to the training sets listbox and update the training data text widget
        if not self.learning_data_dfs[source_number].empty:
            for folder in self.learning_data_dfs[source_number]['folder_path'].unique():
                self.training_sets_listbox.insert(tk.END, folder)
            self.update_training_data_text(source_number)

    def add_training_data(self):
        selected_material = self.selection_var.get()
        if not selected_material:
            messagebox.showwarning("Warning", "Please select a target material.")
            return

        source_number = sc.materials.index(selected_material) + 1
        base_dir = "C:/Users/jonsc690/Documents/BEA-supervisor/SDL_reports"
        folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f)) and "EE_LearnMinimumRate" in f and f"([{source_number}])" in f]

        if not folders:
            messagebox.showwarning("Warning", "No matching folders found.")
            return

        stripped_folders = [f[:9] for f in folders]
        selected_folders = self.select_folders(stripped_folders)
        if not selected_folders:
            return

        for folder in selected_folders:
            full_path = os.path.join(base_dir, folder)
            self.training_sets_listbox.insert(tk.END, full_path)
            self.load_training_data(full_path, source_number)

        self.update_training_data_text(source_number)

    def select_folders(self, folders):
        popup = tk.Toplevel(self.parent)
        popup.title("Select Training Folders")
        popup.geometry("300x400")

        listbox = tk.Listbox(popup, selectmode=tk.MULTIPLE)
        for folder in folders:
            listbox.insert(tk.END, folder)
        listbox.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        def on_ok():
            popup.selected_folders = [folders[i] for i in listbox.curselection()]
            popup.destroy()

        def on_cancel():
            popup.selected_folders = []
            popup.destroy()

        ok_button = ttk.Button(popup, text="OK", command=on_ok)
        ok_button.pack(side=tk.LEFT, padx=10, pady=10)

        cancel_button = ttk.Button(popup, text="Cancel", command=on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=10, pady=10)

        popup.grab_set()
        self.parent.wait_window(popup)

        return popup.selected_folders

    def load_training_data(self, folder, source_number):
        csv_path = os.path.join(folder, "learning_data.csv")
        if not os.path.isfile(csv_path):
            messagebox.showwarning("Warning", f"No learning data found in {folder}.")
            return

        try:
            new_data = pd.read_csv(csv_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading learning data file: {e}")
            return

        if source_number in self.learning_data_dfs and not self.learning_data_dfs[source_number].empty:
            if not self.learning_data_dfs[source_number].columns.equals(new_data.columns):
                messagebox.showerror("Error", "Headers of the learning data files do not match. The new file will not be loaded.")
                return

        new_data['folder_path'] = folder  # Add folder path to the DataFrame for later reference
        if source_number not in self.learning_data_dfs:
            self.learning_data_dfs[source_number] = new_data
        else:
            self.learning_data_dfs[source_number] = pd.concat([self.learning_data_dfs[source_number], new_data], ignore_index=True)

    def update_training_data_text(self, source_number):
        # Clear the text widget
        self.training_data_text.delete(1.0, tk.END)
        # Insert the updated DataFrame contents
        if source_number in self.learning_data_dfs and 'folder_path' in self.learning_data_dfs[source_number].columns:
            self.training_data_text.insert(tk.END, self.learning_data_dfs[source_number].drop(columns='folder_path').to_string(index=False))

    def clear_training_data(self):
        selected_material = self.selection_var.get()
        if not selected_material:
            messagebox.showwarning("Warning", "Please select a target material.")
            return

        source_number = sc.materials.index(selected_material) + 1
        self.learning_data_dfs[source_number] = pd.DataFrame()
        self.training_sets_listbox.delete(0, tk.END)
        self.update_training_data_text(source_number)

    def open_train_model_popup(self):
        popup = tk.Toplevel(self.parent)
        popup.title("Train Model")
        popup.geometry("400x500")

        model_frame = ttk.LabelFrame(popup, text="Random Forest Classifier")
        model_frame.pack(fill=tk.X, padx=10, pady=10)

        # Field names and default values for the Random Forest Classifier
        model_fields = {
            "max_depth": 10,
            "max_leaf_nodes": 250,
            "n_estimators": 25,
            "pool_size": 500,
            "initialisation_runs": 10
        }

        self.model_entries = {}

        # Create entries for each model field
        for i, (field, default) in enumerate(model_fields.items()):
            label = ttk.Label(model_frame, text=field)
            label.grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(model_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, str(default))
            self.model_entries[field] = entry

        evaluation_frame = ttk.LabelFrame(popup, text="Evaluation")
        evaluation_frame.pack(fill=tk.X, padx=10, pady=10)

        # Field names and default values for the Evaluation frame
        evaluation_fields = {
            "CrossVal split fraction": 0.2,
            "mean_threshold": 0.9,
            "std_threshold": 0.1
        }

        self.evaluation_entries = {}

        # Create entries for each evaluation field
        for i, (field, default) in enumerate(evaluation_fields.items()):
            label = ttk.Label(evaluation_frame, text=field)
            label.grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(evaluation_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, str(default))
            self.evaluation_entries[field] = entry

        # Run and Cancel buttons
        button_frame = ttk.Frame(popup)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        run_button = ttk.Button(button_frame, text="Run", command=self.run_model)
        run_button.pack(side=tk.LEFT, padx=5, pady=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=popup.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.model_popup = popup

    def run_model(self):
        model_settings = {field: self.parse_entry_value(entry.get()) for field, entry in self.model_entries.items()}
        evaluation_settings = {field: self.parse_entry_value(entry.get()) for field, entry in self.evaluation_entries.items()}
        model_settings.update(evaluation_settings)
        self.perform_series(model_settings)
        self.open_dashboard()
        self.model_popup.destroy()

    def parse_entry_value(self, value):
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            return value

    def open_model_selection_popup(self):
        popup = tk.Toplevel(self.parent)
        popup.title("Select Model")
        popup.geometry("300x400")

        listbox = tk.Listbox(popup)
        listbox.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        selected_model_var = tk.StringVar()

        selected_material = self.selection_var.get()
        if not selected_material:
            messagebox.showwarning("Warning", "Please select a target material.")
            popup.destroy()
            return

        source_number = sc.materials.index(selected_material) + 1
        base_dir = "C:/Users/jonsc690/Documents/BEA-supervisor/SDL_reports"
        folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f)) and "EE_LearnMinimumRate" in f and f"([{source_number}])" in f]

        stripped_folders = [f[:9] for f in folders]

        for folder in stripped_folders:
            listbox.insert(tk.END, folder)

        def on_ok():
            selection = listbox.curselection()
            if selection:
                selected_model_var.set(listbox.get(selection[0]))
                self.display_model_in_viewer(selected_model_var.get())
                self.selected_model_name = selected_model_var.get()  # Store the selected model name
                self.bind_current_model_button.config(state=tk.NORMAL)  # Enable bind button
            popup.destroy()

        def on_cancel():
            popup.destroy()

        ok_button = ttk.Button(popup, text="OK", command=on_ok)
        ok_button.pack(side=tk.LEFT, padx=10, pady=10)

        cancel_button = ttk.Button(popup, text="Cancel", command=on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=10, pady=10)

        popup.grab_set()
        self.parent.wait_window(popup)

    def display_model_in_viewer(self, model_name):
        selected_material = self.selection_var.get()
        if not selected_material:
            messagebox.showwarning("Warning", "Please select a target material.")
            return

        for widget in self.model_viewer_canvas.winfo_children():
            widget.destroy()

        label = ttk.Label(self.model_viewer_canvas, text=model_name)
        label.pack(pady=10)

        # Placeholder function to generate and display plots
        self.generate_model_plots(model_name, selected_material)

    def generate_model_plots(self, model_name, selected_material):
        # Placeholder for generating plots
        print(f"Generating plots for model: {model_name} and material: {selected_material}")

        # Example: Create a placeholder label for where the plot will be displayed
        plot_label = ttk.Label(self.model_viewer_canvas, text=f"Plot for {model_name} and material: {selected_material}")
        plot_label.pack(pady=10)

        # TODO: Implement the actual plotting logic here

    def bind_current_model(self):
        selected_material = self.selection_var.get()
        if hasattr(self, 'selected_model_name') and selected_material:
            source_key = f"EE_LearnMinimumRate_model_{selected_material}"
            if source_key in self.workflow_data:
                messagebox.showwarning("Warning", f"There is already a model bound to this workflow for {selected_material}.")
            else:
                self.workflow_data[source_key] = self.selected_model_name
                self.workflow_window.save_workflow()  # Call save_workflow through the WorkflowWindow reference
                messagebox.showinfo("Model Bound", f"Model '{self.selected_model_name}' has been bound to the workflow for {selected_material}.")
                self.update_bound_model_label(selected_material)
                self.re_evaluate_model_button.config(state=tk.NORMAL)
        else:
            messagebox.showwarning("Warning", "No model selected to bind.")

    def re_evaluate_model(self):
        # Add functionality to re-evaluate the model
        print("Re-evaluate model")

    def perform_series(self, model_settings):
        print(f"Performing series with settings: {model_settings}")
        # Placeholder for the actual implementation
        pass

    def open_dashboard(self):
        dashboard_popup = tk.Toplevel(self.parent)
        dashboard_popup.title("Dashboard")
        dashboard_popup.geometry("600x400")
        ttk.Label(dashboard_popup, text="Dashboard - Placeholder").pack(pady=20)
        # Placeholder for the actual implementation


class LearnSputterProcessTab:
    def __init__(self, parent, workflow_data, workflow_window):
        self.parent = parent
        self.workflow_data = workflow_data
        self.workflow_window = workflow_window  # Store the reference to the WorkflowWindow instance
        self.target_materials = []
        self.source_numbers = []
        self.learning_data_dfs = {}  # Initialize a dictionary to store DataFrames for each source_number
        self.create_widgets()
        self.populate_dropdown()

    def create_widgets(self):
        # Main frame for the tab
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Dropdown selection field
        self.selection_label = ttk.Label(self.frame, text="Select Target Material:")
        self.selection_label.pack(pady=5)

        self.selection_var = tk.StringVar()
        self.selection_dropdown = ttk.Combobox(self.frame, textvariable=self.selection_var)
        self.selection_dropdown.pack(pady=5)
        self.selection_dropdown.bind("<<ComboboxSelected>>", self.on_dropdown_selection)

        self.bound_model_label = ttk.Label(self.frame, text="No model bound")
        self.bound_model_label.pack(pady=5)

        # SJ_LearnSputterProcess frame
        self.sp_frame = ttk.LabelFrame(self.frame, text="SJ_LearnSputterProcess")
        self.sp_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Buttons in the SJ_LearnSputterProcess frame
        self.add_training_data_button = ttk.Button(self.sp_frame, text="Add training data", command=self.add_training_data)
        self.add_training_data_button.pack(fill=tk.X, pady=5)

        self.clear_training_data_button = ttk.Button(self.sp_frame, text="Clear training data", command=self.clear_training_data)
        self.clear_training_data_button.pack(fill=tk.X, pady=5)

        self.train_new_model_button = ttk.Button(self.sp_frame, text="Train new model", command=self.open_train_model_popup)
        self.train_new_model_button.pack(fill=tk.X, pady=5)

        self.view_load_models_button = ttk.Button(self.sp_frame, text="View/load models", command=self.open_model_selection_popup)
        self.view_load_models_button.pack(fill=tk.X, pady=5)

        self.bind_current_model_button = ttk.Button(self.sp_frame, text="Bind current model", command=self.bind_current_model, state=tk.DISABLED)
        self.bind_current_model_button.pack(fill=tk.X, pady=5)

        self.re_evaluate_model_button = ttk.Button(self.sp_frame, text="Re-evaluate model", command=self.re_evaluate_model, state=tk.DISABLED)
        self.re_evaluate_model_button.pack(fill=tk.X, pady=5)

        # Training sets field
        self.training_sets_label = ttk.Label(self.sp_frame, text="Training Sets")
        self.training_sets_label.pack(pady=5)
        self.training_sets_listbox = tk.Listbox(self.sp_frame)
        self.training_sets_listbox.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Model viewer frame
        self.model_viewer_frame = ttk.LabelFrame(self.frame, text="Model Viewer")
        self.model_viewer_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.model_viewer_canvas = tk.Canvas(self.model_viewer_frame)
        self.model_viewer_canvas.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Training data frame
        self.training_data_frame = ttk.LabelFrame(self.frame, text="Training Data")
        self.training_data_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.training_data_text = tk.Text(self.training_data_frame, wrap=tk.NONE)
        self.training_data_text.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Add scrollbars to the training data text widget
        self.scroll_x = ttk.Scrollbar(self.training_data_frame, orient=tk.HORIZONTAL, command=self.training_data_text.xview)
        self.scroll_y = ttk.Scrollbar(self.training_data_frame, orient=tk.VERTICAL, command=self.training_data_text.yview)
        self.training_data_text.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    def reset_state(self):
        self.selection_var.set('')
        self.bound_model_label.config(text="No model bound")
        self.training_sets_listbox.delete(0, tk.END)
        self.training_data_text.delete(1.0, tk.END)
        for widget in self.model_viewer_canvas.winfo_children():
            widget.destroy()
        self.bind_current_model_button.config(state=tk.DISABLED)
        self.re_evaluate_model_button.config(state=tk.DISABLED)
        self.learning_data_dfs.clear()  # Clear learning data
        self.populate_dropdown()  # Refresh the dropdown

    def populate_dropdown(self):
        # Extract target materials and source numbers based on active sources
        print(f"Populating dropdown with workflow data: {self.workflow_data}")
        target_materials = self.workflow_data.get("target materials", [])
        active_sources = self.workflow_data.get("active_sources", [])

        self.target_materials = [material for i, material in enumerate(target_materials) if active_sources[i]]
        self.source_numbers = [i + 1 for i, active in enumerate(active_sources) if active]

        print(f"Target materials: {self.target_materials}")
        self.selection_dropdown['values'] = self.target_materials
        self.selection_dropdown.set('')  # Clear the current selection

    def update_workflow_data(self, workflow_data):
        self.workflow_data = workflow_data
        self.populate_dropdown()

    def on_dropdown_selection(self, event):
        selected_material = self.selection_var.get()
        if not selected_material:
            return

        source_number = sc.materials.index(selected_material) + 1
        self.display_training_data(source_number)
        self.update_bound_model_label(selected_material)

        source_key = f"SJ_LearnSputterProcess_model_{selected_material}"
        if source_key in self.workflow_data:
            self.re_evaluate_model_button.config(state=tk.NORMAL)
        else:
            self.re_evaluate_model_button.config(state=tk.DISABLED)

        # Clear current model name and deactivate bind button
        self.bound_model_label.config(text="No model bound")
        self.bind_current_model_button.config(state=tk.DISABLED)


    def update_bound_model_label(self, selected_material):
        source_key = f"SJ_LearnSputterProcess_model_{selected_material}"
        if source_key in self.workflow_data:
            bound_model = self.workflow_data[source_key]
            self.bound_model_label.config(text=f"Bound model for {selected_material}: {bound_model}")
        else:
            self.bound_model_label.config(text=f"No model bound for {selected_material}")

    def display_training_data(self, source_number):
        if source_number not in self.learning_data_dfs:
            self.learning_data_dfs[source_number] = pd.DataFrame()

        self.training_sets_listbox.delete(0, tk.END)
        self.training_data_text.delete(1.0, tk.END)

        # Add entries to the training sets listbox and update the training data text widget
        if not self.learning_data_dfs[source_number].empty:
            for folder in self.learning_data_dfs[source_number]['folder_path'].unique():
                self.training_sets_listbox.insert(tk.END, folder)
            self.update_training_data_text(source_number)

    def add_training_data(self):
        selected_material = self.selection_var.get()
        if not selected_material:
            messagebox.showwarning("Warning", "Please select a target material.")
            return

        source_number = sc.materials.index(selected_material) + 1
        base_dir = "C:/Users/jonsc690/Documents/BEA-supervisor/SDL_reports"
        folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f)) and "SJ_LearnSputterProcess" in f and f"([{source_number}])" in f]

        if not folders:
            messagebox.showwarning("Warning", "No matching folders found.")
            return

        stripped_folders = [f[:9] for f in folders]
        selected_folders = self.select_folders(stripped_folders)
        if not selected_folders:
            return

        for folder in selected_folders:
            full_path = os.path.join(base_dir, folder)
            self.training_sets_listbox.insert(tk.END, full_path)
            self.load_training_data(full_path, source_number)

        self.update_training_data_text(source_number)

    def select_folders(self, folders):
        popup = tk.Toplevel(self.parent)
        popup.title("Select Training Folders")
        popup.geometry("300x400")

        listbox = tk.Listbox(popup, selectmode=tk.MULTIPLE)
        for folder in folders:
            listbox.insert(tk.END, folder)
        listbox.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        def on_ok():
            popup.selected_folders = [folders[i] for i in listbox.curselection()]
            popup.destroy()

        def on_cancel():
            popup.selected_folders = []
            popup.destroy()

        ok_button = ttk.Button(popup, text="OK", command=on_ok)
        ok_button.pack(side=tk.LEFT, padx=10, pady=10)

        cancel_button = ttk.Button(popup, text="Cancel", command=on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=10, pady=10)

        popup.grab_set()
        self.parent.wait_window(popup)

        return popup.selected_folders

    def load_training_data(self, folder, source_number):
        csv_path = os.path.join(folder, "learning_data.csv")
        if not os.path.isfile(csv_path):
            messagebox.showwarning("Warning", f"No learning data found in {folder}.")
            return

        try:
            new_data = pd.read_csv(csv_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading learning data file: {e}")
            return

        if source_number in self.learning_data_dfs and not self.learning_data_dfs[source_number].empty:
            if not self.learning_data_dfs[source_number].columns.equals(new_data.columns):
                messagebox.showerror("Error", "Headers of the learning data files do not match. The new file will not be loaded.")
                return

        new_data['folder_path'] = folder  # Add folder path to the DataFrame for later reference
        if source_number not in self.learning_data_dfs:
            self.learning_data_dfs[source_number] = new_data
        else:
            self.learning_data_dfs[source_number] = pd.concat([self.learning_data_dfs[source_number], new_data], ignore_index=True)

    def update_training_data_text(self, source_number):
        # Clear the text widget
        self.training_data_text.delete(1.0, tk.END)
        # Insert the updated DataFrame contents
        if source_number in self.learning_data_dfs and 'folder_path' in self.learning_data_dfs[source_number].columns:
            self.training_data_text.insert(tk.END, self.learning_data_dfs[source_number].drop(columns='folder_path').to_string(index=False))

    def clear_training_data(self):
        selected_material = self.selection_var.get()
        if not selected_material:
            messagebox.showwarning("Warning", "Please select a target material.")
            return

        source_number = sc.materials.index(selected_material) + 1
        self.learning_data_dfs[source_number] = pd.DataFrame()
        self.training_sets_listbox.delete(0, tk.END)
        self.update_training_data_text(source_number)

    def open_train_model_popup(self):
        popup = tk.Toplevel(self.parent)
        popup.title("Train Model")
        popup.geometry("400x500")

        model_frame = ttk.LabelFrame(popup, text="Random Forest Classifier")
        model_frame.pack(fill=tk.X, padx=10, pady=10)

        # Field names and default values for the Random Forest Classifier
        model_fields = {
            "max_depth": 15,
            "min_samples_split": 2,
            "n_estimators": 50,
            "min_samples_leaf": 1,
            "max_features": 'auto'
        }

        self.model_entries = {}

        # Create entries for each model field
        for i, (field, default) in enumerate(model_fields.items()):
            label = ttk.Label(model_frame, text=field)
            label.grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(model_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, str(default))
            self.model_entries[field] = entry

        evaluation_frame = ttk.LabelFrame(popup, text="Evaluation")
        evaluation_frame.pack(fill=tk.X, padx=10, pady=10)

        # Field names and default values for the Evaluation frame
        evaluation_fields = {
            "CrossVal split fraction": 0.3,
            "mean_threshold": 0.85,
            "std_threshold": 0.15
        }

        self.evaluation_entries = {}

        # Create entries for each evaluation field
        for i, (field, default) in enumerate(evaluation_fields.items()):
            label = ttk.Label(evaluation_frame, text=field)
            label.grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(evaluation_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, str(default))
            self.evaluation_entries[field] = entry

        # Run and Cancel buttons
        button_frame = ttk.Frame(popup)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        run_button = ttk.Button(button_frame, text="Run", command=self.run_model)
        run_button.pack(side=tk.LEFT, padx=5, pady=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=popup.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.model_popup = popup

    def run_model(self):
        model_settings = {field: self.parse_entry_value(entry.get()) for field, entry in self.model_entries.items()}
        evaluation_settings = {field: self.parse_entry_value(entry.get()) for field, entry in self.evaluation_entries.items()}
        model_settings.update(evaluation_settings)
        self.perform_series(model_settings)
        self.open_dashboard()
        self.model_popup.destroy()

    def parse_entry_value(self, value):
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            return value

    def open_model_selection_popup(self):
        popup = tk.Toplevel(self.parent)
        popup.title("Select Model")
        popup.geometry("300x400")

        listbox = tk.Listbox(popup)
        listbox.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        selected_model_var = tk.StringVar()

        selected_material = self.selection_var.get()
        if not selected_material:
            messagebox.showwarning("Warning", "Please select a target material.")
            popup.destroy()
            return

        source_number = sc.materials.index(selected_material) + 1
        base_dir = "C:/Users/jonsc690/Documents/BEA-supervisor/SDL_reports"
        folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f)) and "SJ_LearnSputterProcess" in f and f"([{source_number}])" in f]

        stripped_folders = [f[:9] for f in folders]

        for folder in stripped_folders:
            listbox.insert(tk.END, folder)

        def on_ok():
            selection = listbox.curselection()
            if selection:
                selected_model_var.set(listbox.get(selection[0]))
                self.display_model_in_viewer(selected_model_var.get())
                self.selected_model_name = selected_model_var.get()  # Store the selected model name
                self.bind_current_model_button.config(state=tk.NORMAL)  # Enable bind button
            popup.destroy()

        def on_cancel():
            popup.destroy()

        ok_button = ttk.Button(popup, text="OK", command=on_ok)
        ok_button.pack(side=tk.LEFT, padx=10, pady=10)

        cancel_button = ttk.Button(popup, text="Cancel", command=on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=10, pady=10)

        popup.grab_set()
        self.parent.wait_window(popup)

    def display_model_in_viewer(self, model_name):
        selected_material = self.selection_var.get()
        if not selected_material:
            messagebox.showwarning("Warning", "Please select a target material.")
            return

        for widget in self.model_viewer_canvas.winfo_children():
            widget.destroy()

        label = ttk.Label(self.model_viewer_canvas, text=model_name)
        label.pack(pady=10)

        # Placeholder function to generate and display plots
        self.generate_model_plots(model_name, selected_material)

    def generate_model_plots(self, model_name, selected_material):
        # Placeholder for generating plots
        print(f"Generating plots for model: {model_name} and material: {selected_material}")

        # Example: Create a placeholder label for where the plot will be displayed
        plot_label = ttk.Label(self.model_viewer_canvas, text=f"Plot for {model_name} and material: {selected_material}")
        plot_label.pack(pady=10)

        # TODO: Implement the actual plotting logic here

    def bind_current_model(self):
        selected_material = self.selection_var.get()
        if hasattr(self, 'selected_model_name') and selected_material:
            source_key = f"SJ_LearnSputterProcess_model_{selected_material}"
            if source_key in self.workflow_data:
                messagebox.showwarning("Warning", f"There is already a model bound to this workflow for {selected_material}.")
            else:
                self.workflow_data[source_key] = self.selected_model_name
                self.workflow_window.save_workflow()  # Call save_workflow through the WorkflowWindow reference
                messagebox.showinfo("Model Bound", f"Model '{self.selected_model_name}' has been bound to the workflow for {selected_material}.")
                self.update_bound_model_label(selected_material)
                self.re_evaluate_model_button.config(state=tk.NORMAL)
        else:
            messagebox.showwarning("Warning", "No model selected to bind.")

    def re_evaluate_model(self):
        # Add functionality to re-evaluate the model
        print("Re-evaluate model")

    def perform_series(self, model_settings):
        print(f"Performing series with settings: {model_settings}")
        # Placeholder for the actual implementation
        pass

    def open_dashboard(self):
        dashboard_popup = tk.Toplevel(self.parent)
        dashboard_popup.title("Dashboard")
        dashboard_popup.geometry("600x400")
        ttk.Label(dashboard_popup, text="Dashboard - Placeholder").pack(pady=20)
        # Placeholder for the actual implementation


if __name__ == "__main__":
    app = BerthaGUI()
    app.mainloop()
