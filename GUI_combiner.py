import customtkinter as ctk
from PIL import Image
import webbrowser
import combiner
import scheduler
import subject_parser
from typing import List
import openpyxl as xl
from tkinter import ttk
from CTkTable import CTkTable

# Default appearance mode
ctk.set_appearance_mode('light')

# IMPORTANT CONSTANTS
SUBJECT_DIR = 'subjects'
ICON_PATH = r'./assets/images/logo.ico'
FULL_SCREEN = False
INITIAL_RESOLUTION_POSITION = '1200x800+5+5'
LOGO_PATH = r'./assets/images/logo.png'
REP_URL = r'https://github.com/gonzagrau/Combinador-PSICO-UBA'
REP_TEXT = 'Ver en GitHub'
TITLE = 'PsiComb'
VER_STR = 'Ver. 1.0'
LIGHT_MODE_TEXT = 'Modo dia'
DARK_MODE_TEXT = 'Modo noche'
CHOOSE_TEXT = 'Elija sus comisiones para cada materia'
WELCOME_TEXT = 'Combinador de horarios \n Psicología UBA'
COMBINE_BUTTON_TEXT = 'Calcular combinaciones'
SEL_ALL_TEXT = 'Seleccionar todas'
DESEL_ALL_TEXT = 'Deseleccionar todas'
OUTPUT_PATH = 'output_excels/combinations.xlsx'

# Shortcut for fast padding
padding = dict(padx=5, pady=5)


# Class definitions for UI
class MainWindow(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title(TITLE)
        self.iconbitmap(ICON_PATH)
        if FULL_SCREEN:
            self.geometry("%dx%d+0+0" %(self.winfo_screenwidth(), self.winfo_screenheight()))
        else:
            self.geometry(INITIAL_RESOLUTION_POSITION)

        # self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Setting properties
        self.current_frame = MainFrame(self)
        # self.state('zoomed') # This is not working

        # Setting closing protocol
        self.protocol("WM_DELETE_WINDOW", self._quit_me)

    def _quit_me(self):
    # This ensures that the program stops when the main window is closed
        print('quit')
        self.quit()
        self.destroy()

    @property
    def current_frame(self):
        return self._current_frame

    @current_frame.setter
    def current_frame(self, frame):
        try:
            self._current_frame.destroy()
        except AttributeError:
            pass
        self._current_frame = frame
        self._current_frame.grid(row=0, column=0, sticky="nsew")

    @current_frame.getter
    def current_frame(self):
        return self._current_frame


class MainFrame(ctk.CTkFrame):
    """
    This frame includes: the program logo, a button to access the combiner.
    a version label, a dark/light mode switch, and a GitHub link button.
    """

    def __init__(self, master: MainWindow, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        self.rowconfigure(0, weight=10)
        self.rowconfigure(1, weight=10)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # Logo image
        self.logo_image = ctk.CTkImage(light_image=Image.open(LOGO_PATH),
                                       dark_image=Image.open(LOGO_PATH),
                                       size=(300, 250))
        self.logo_button = ctk.CTkButton(self,
                                         image=self.logo_image,
                                         fg_color='transparent',
                                         bg_color='transparent',
                                         text='',
                                         hover=False)
        self.logo_button.grid(row=0, column=1, columnspan=1, sticky='nsew')

        # Combiner button
        self.button_combiner = ctk.CTkButton(master=self,
                                             text=WELCOME_TEXT,
                                             fg_color=('purple', 'purple'),
                                             text_color='white',
                                             font=('courier', 20, 'bold'),
                                             command=self.button_combiner_action)
        self.button_combiner.grid(row=1, column=1, columnspan=1, sticky='ew')

        # Version string label
        self.version_str = ctk.CTkLabel(self, text=VER_STR)
        self.version_str.grid(row=2, column=0, sticky='ew')

        # Switch mode button
        self.mode_switch_var = ctk.BooleanVar(self, True)
        self.mode_switch = ctk.CTkSwitch(self,
                                         variable=self.mode_switch_var,
                                         command=self.mode_switch_action,
                                         progress_color=('white', 'gray'),
                                         onvalue=True, offvalue=False)
        if ctk.get_appearance_mode() == 'Dark':
            self.mode_switch.deselect()
            self.mode_switch.configure(text=LIGHT_MODE_TEXT)
        else:
            self.mode_switch.select()
            self.mode_switch.configure(text=LIGHT_MODE_TEXT)
        self.mode_switch.grid(row=2, column=1)

        # View repository button
        def go_to_repo():
            webbrowser.open_new(REP_URL)

        self.but_view_repo = ctk.CTkButton(self,
                                           text=REP_TEXT,
                                           text_color=('black', 'white'),
                                           command=go_to_repo,
                                           fg_color='transparent')
        self.but_view_repo.grid(row=2, column=2)

    def mode_switch_action(self):
        light = self.mode_switch_var.get()
        if light:
            ctk.set_appearance_mode('light')
            self.mode_switch.configure(text=LIGHT_MODE_TEXT)
        else:
            ctk.set_appearance_mode("dark")
            self.mode_switch.configure(text=DARK_MODE_TEXT)

    def button_combiner_action(self):
        self.master.current_frame = CombinerFrame(self.master)


class CombinerFrame(ctk.CTkFrame):
    def __init__(self, master: MainWindow, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.subjects = subject_parser.parse_all_subjects(SUBJECT_DIR)

        # Subjects found label
        self.choose_label = ctk.CTkLabel(master=self,
                                         text=CHOOSE_TEXT,
                                         font=('helvetica', 20, 'bold'),
                                         anchor='center',
                                         text_color=('black', 'white'))
        # self.frame_label.grid(row=0, column=0, sticky='ew', **padding)
        self.choose_label.pack(fill=ctk.X, side=ctk.TOP, **padding)

        # Comission selector
        self.selector_list = []
        self.selector_frame = ctk.CTkFrame(self)
        for subject in self.subjects:
            self.add_selector(subject)
        self.selector_frame.pack(fill=ctk.BOTH, side=ctk.TOP, expand=True, **padding)

        # Combine button
        self.combine_button = ctk.CTkButton(master=self,
                                            text=COMBINE_BUTTON_TEXT,
                                            command=self.combine_action,
                                            height=35,
                                            font=('roboto', 25, 'bold'),
                                            text_color=('black', 'white'),
                                            fg_color=('lightgreen', 'darkgreen'))
        self.combine_button.pack(side=ctk.TOP, pady=25)

    def add_selector(self, subject):
        selector = ComissionSelectorFrame(self.selector_frame, subject)
        selector.pack(expand=True, fill=ctk.BOTH, side=ctk.LEFT, **padding)
        self.selector_list.append(selector)

    def combine_action(self):
        combinations = combiner.find_combinations(self.subjects)
        scheduler.save_to_excel(self.subjects, combinations, OUTPUT_PATH)
        self.master.current_frame = DisplayCombFrame(self.master, self.subjects, combinations)



class ComissionSelectorFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, subject:combiner.Subject, **kwargs):
        super().__init__(master, **kwargs)

        # grid configuration
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.row_counter = 0

        # subject label
        self.subject_label = ctk.CTkLabel(master=self,
                                          text=subject.name,
                                          font=('arial', 20, 'bold'),
                                          bg_color='lightblue',
                                          text_color='black',
                                          corner_radius=20,
                                          anchor='center')
        self.subject_label.grid(row=self.row_counter, column=0, columnspan=2, **padding)
        self.row_counter += 1

        # select all radio buttons
        self.radio_var = ctk.BooleanVar(value=True)
        self.sel_all_radio = ctk.CTkRadioButton(master=self,
                                                text=SEL_ALL_TEXT,
                                                variable=self.radio_var,
                                                command=self.sel_radio_action,
                                                value=1,
                                                fg_color='purple')
        self.desel_all_radio = ctk.CTkRadioButton(master=self,
                                                  text=DESEL_ALL_TEXT,
                                                  variable=self.radio_var,
                                                  command=self.desel_radio_action,
                                                  value=0,
                                                  fg_color='purple')
        self.sel_all_radio.grid(row=self.row_counter, column=0, **padding)
        self.desel_all_radio.grid(row=self.row_counter, column=1, **padding)
        self.row_counter += 1

        # checkboxes
        self.checkbox_list = []
        self.comission_labels = []
        for comission in subject.comission_list:
            self.add_comission_checkbox(comission)

    def add_comission_checkbox(self, comission):
        # label for each comission
        com_label = ctk.CTkLabel(master=self,
                                      text=f"COMISION {comission.identifyer}",
                                      font=('helvetica', 13, 'bold'))
        com_label.grid(row=self.row_counter, column=0, columnspan=2, pady=(0, 10), sticky='w')
        self.row_counter += 1
        self.comission_labels.append(com_label)

        # actual checkbox
        checkbox = ComissionCheckbox(self, comission)
        checkbox.grid(row=self.row_counter, column=0, columnspan=2, pady=(0, 10), sticky='w')
        self.row_counter += 1
        self.checkbox_list.append(checkbox)

    def sel_radio_action(self):
        for checkbox in self.checkbox_list:
            checkbox.select()
            checkbox.toggle_comission()

    def desel_radio_action(self):
        for checkbox in self.checkbox_list:
            checkbox.deselect()
            checkbox.toggle_comission()


class ComissionCheckbox(ctk.CTkCheckBox):
    def __init__(self, master, comission: combiner.Comission, **kwargs):
        super().__init__(master, **kwargs)
        self.comission = comission
        self.check_var = ctk.BooleanVar(value=True)
        self.configure(text=comission.blocks_str(),
                       command=self.toggle_comission,
                       variable=self.check_var,
                       font=('helvetica', 12) )
    def toggle_comission(self):
        if self.check_var.get():
            self.comission.select()
        else:
            self.comission.deselect()


class DisplayCombFrame(ctk.CTkFrame):
    def __init__(self, master, subjects: List[combiner.Subject], combinations: List[combiner.Combination], **kwargs):
        super().__init__(master, **kwargs)
        self.subjects = subjects
        self.combinations = combinations

        # grid configuration
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=9)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)

        # go back button
        self.go_back_button = ctk.CTkButton(master=self,
                                            text='<',
                                            command=self.go_back_to_combiner,
                                            width=15,
                                            height=15,
                                            corner_radius=15,
                                            fg_color='purple')
        self.go_back_button.grid(row=0, column=0)

        # combinations found label
        self.comb_found_label = ctk.CTkLabel(master=self,
                                             text=f"{len(combinations)} combinaciones halladas",
                                             font=('helvetica', 20, 'italic'),
                                             anchor='center')
        self.comb_found_label.grid(row=0, column=1, sticky='e')

        # table
        table_values = [[subject.name for subject in self.subjects]]
        for comb in self.combinations:
            table_values.append([com.identifyer for com in comb])
        self.table = CTkTable(master=self,
                              header_color='lightgreen',
                              values=table_values)
        self.table.grid(row=1, column=0, columnspan=2, padx=20, pady=20)


    def go_back_to_combiner(self):
        self.master.current_frame = CombinerFrame(self.master)



def main():
    root = MainWindow()
    root.mainloop()


if __name__ == '__main__':
    main()