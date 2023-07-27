import customtkinter as ctk
from PIL import Image
import webbrowser
import combiner
import scheduler
import subject_parser
from typing import List
from CTkTable import CTkTable
import subprocess, os, platform

# File opening protocol
if platform.system() == 'Darwin':       # macOS
    launch_file = lambda filepath: subprocess.call(('open', filepath))
elif platform.system() == 'Windows':    # Windows
    launch_file = lambda filepath: os.startfile(filepath)
else:                                   # linux variants
    launch_file = lambda filepath: subprocess.call(('xdg-open', filepath))

# Default appearance mode
ctk.set_appearance_mode('light')

# IMPORTANT FILE CONSTANTS
SUBJECT_DIR = 'subjects'
ICON_PATH = r'./assets/images/logo.ico'
FULL_SCREEN = False
INITIAL_RESOLUTION_POSITION = '1200x800+5+5'
LOGO_PATH = r'./assets/images/logo.png'
PSI_ICON_PATH = r'./assets/images/psi_rojo_30x30.png'
DEL_ICON_PATH = r'./assets/images/delete_icon.png'
REP_URL = r'https://github.com/gonzagrau/Combinador-PSICO-UBA'
CAMPUS_URL = r'http://academica.psi.uba.ar/index.php'
OUTPUT_PATH = r"combinations.xlsx"

# STRING CONSTANTS
LINK_ENTRY_TEXT = 'Ingrese el link de la materia a agregar'
ADD_SUB_TEXT = 'Agregar materia'
SUB_TABLES_TEXT = 'Materias elegidas'
REP_TEXT = 'Ver en GitHub'
TITLE = 'PsiComb'
VER_STR = 'Ver. 1.1'
LIGHT_MODE_TEXT = 'Modo dia'
DARK_MODE_TEXT = 'Modo noche'
CHOOSE_TEXT = 'Elija sus comisiones para cada materia'
GO_TO_SELECTOR_TEXT = 'Ir al selector de comisiones'
COMBINE_BUTTON_TEXT = 'Calcular combinaciones'
SEL_ALL_TEXT = 'Seleccionar todas'
DESEL_ALL_TEXT = 'Deseleccionar todas'
LAUNCH_TEXT = 'Ver horarios completos en Excel'

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

    def __init__(self, master: MainWindow, subjects: List[combiner.Subject] = None,**kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        # Grid configure
        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=5)
        self.rowconfigure(2, weight=10)
        self.rowconfigure(3, weight=5)
        self.rowconfigure(4, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # Inputted subjects
        if subjects is not None:
            self.subjects_list = subjects
        else:
            self.subjects_list = []

        ################################################
        # ----------------ROW 0-------------------------
        ################################################

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

        ################################################
        # ----------------ROW 1-------------------------
        ################################################

        # New subject entry and button
        self.link_entry = ctk.CTkEntry(master=self,
                                       placeholder_text=LINK_ENTRY_TEXT,
                                       #width=600,
                                       height=50,
                                       border_width=2,
                                       corner_radius=10)
        self.link_entry.grid(row=1, column=1, sticky='ew')

        self.add_sub_button = ctk.CTkButton(master=self,
                                            text='+',
                                            font=('arial', 24, 'bold'),
                                            width=50,
                                            height=50,
                                            command=self.add_subject_action,
                                            fg_color=('purple', 'purple'))
        self.add_sub_button.grid(row=1, column=2, sticky='w', **padding)

        ################################################
        # ----------------ROW 2-------------------------
        ################################################

        # Campus link button
        self.psi_icon = ctk.CTkImage(light_image=Image.open(PSI_ICON_PATH),
                                     dark_image=Image.open(PSI_ICON_PATH),
                                     size=(40, 40))
        def go_to_campus():
            webbrowser.open_new(CAMPUS_URL)
        self.campus_link_button = ctk.CTkButton(master=self,
                                                text='',
                                                corner_radius=10,
                                                image=self.psi_icon,
                                                fg_color='transparent',
                                                bg_color='transparent',
                                                height=40,
                                                width=40,
                                                command=go_to_campus)
        self.campus_link_button.grid(row=1, column=0, sticky='e', **padding)

        # Subject table
        self.subjects_table = CTkTable(master=self,
                                       header_color='lightgreen',
                                       font=('helvetica', 12, 'bold'),
                                       values=[[SUB_TABLES_TEXT]])
        self.subjects_table.grid(row=2, column=1, sticky='new')
        for new_sub in self.subjects_list:
            self.subjects_table.add_row([new_sub.name])

        # Delete button
        self.del_image = ctk.CTkImage(light_image=Image.open(DEL_ICON_PATH),
                                       dark_image=Image.open(DEL_ICON_PATH),
                                       size=(20, 20))
        self.subject_del_button = ctk.CTkButton(master=self,
                                                text='',
                                                corner_radius=10,
                                                image=self.del_image,
                                                fg_color='transparent',
                                                height=20,
                                                width=20,
                                                command=self.delete_subject)
        self.subject_del_button.grid(row=2, column=2, sticky='nw', padx=5)

        ################################################
        # ----------------ROW 3-------------------------
        ################################################

        # Combiner button
        self.button_combiner = ctk.CTkButton(master=self,
                                             text=GO_TO_SELECTOR_TEXT,
                                             fg_color=('purple', 'purple'),
                                             text_color='white',
                                             font=('helvetica', 20, 'bold'),
                                             command=self.goto_combiner_action)
        self.button_combiner.grid(row=3, column=1, columnspan=1, sticky='ew')

        ################################################
        # ----------------ROW 4-------------------------
        ################################################

        # Version string label
        self.version_str = ctk.CTkLabel(self, text=VER_STR)
        self.version_str.grid(row=4, column=0, sticky='ew')

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
        self.mode_switch.grid(row=4, column=1)

        # View repository button
        def go_to_repo():
            webbrowser.open_new(REP_URL)

        self.but_view_repo = ctk.CTkButton(self,
                                           text=REP_TEXT,
                                           text_color=('black', 'white'),
                                           command=go_to_repo,
                                           fg_color='transparent')
        self.but_view_repo.grid(row=4, column=2)


    def add_subject_action(self):
        # html parse
        new_url = self.link_entry.get()
        new_sub = subject_parser.url_parse(new_url)
        self.subjects_list.append(new_sub)

        # clear entry and add to table
        self.link_entry.delete(0, len(new_url))
        self.subjects_table.add_row([new_sub.name])

    def delete_subject(self):
        try:
            self.subjects_list.pop()
            self.subjects_table.delete_row(len(self.subjects_list)+1)
        except IndexError:
            pass

    def mode_switch_action(self):
        light = self.mode_switch_var.get()
        if light:
            ctk.set_appearance_mode('light')
            self.mode_switch.configure(text=LIGHT_MODE_TEXT)
        else:
            ctk.set_appearance_mode("dark")
            self.mode_switch.configure(text=DARK_MODE_TEXT)

    def goto_combiner_action(self):
        self.master.current_frame = CombinerFrame(self.master, subjects=self.subjects_list)


class CombinerFrame(ctk.CTkFrame):
    def __init__(self, master: MainWindow, subjects: List[combiner.Subject], **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.subjects = subjects

        # go back button
        self.go_back_button = GoBackButton(self)
        self.go_back_button.pack(side=ctk.TOP, **padding)
        # Subjects found label
        self.choose_label = ctk.CTkLabel(master=self,
                                         text=CHOOSE_TEXT,
                                         font=('helvetica', 20, 'bold'),
                                         anchor='center',
                                         text_color=('black', 'white'))
        # self.frame_label.grid(row=0, column=0, sticky='ew', **padding)
        self.choose_label.pack(side=ctk.TOP, **padding)

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
        self.radio_var = ctk.BooleanVar(value=False)
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

        self.desel_radio_action()

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


class DisplayCombFrame(ctk.CTkScrollableFrame):
    def __init__(self, master: MainWindow, subjects: List[combiner.Subject], combinations: List[combiner.Combination], **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.subjects = subjects
        self.combinations = combinations
        self.schedules = []
        for combination in self.combinations:
            new_sched = scheduler.Schedule(freq='60T')
            new_sched.add_combination(self.subjects, combination)
            self.schedules.append(new_sched)

        # grid configuration
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=6)
        self.rowconfigure(2, weight=3)
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
        def found_str(l: List):
            if not len(l):
                return 'Ninguna combinación hallada'
            elif len(l) == 1:
                return '1 combinación hallada'
            return f"{len(l)} combinaciones halladas"

        self.comb_found_label = ctk.CTkLabel(master=self,
                                             text=found_str(self.combinations),
                                             font=('helvetica', 18, 'bold'),
                                             anchor='center')
        self.comb_found_label.grid(row=0, column=1)

        # Schedule tabview
        self.schedules_tabs = ScheduleTabView(self, self.schedules)
        self.schedules_tabs.grid(row=1, column=0, columnspan=2, padx=20, pady=20)

        # launch excel file
        def launch_action():
            launch_file(os.path.abspath(OUTPUT_PATH))
        self.launch_button = ctk.CTkButton(master=self,
                                           text=LAUNCH_TEXT,
                                           command=launch_action,
                                           height=35,
                                           font=('roboto', 25, 'bold'),
                                           text_color=('black', 'white'),
                                           fg_color=('lightgreen', 'darkgreen'))
        self.launch_button.grid(row=2, column=0, columnspan=2, padx=20, pady=20)


    def go_back_to_combiner(self):
        self.master.current_frame = CombinerFrame(self.master, self.subjects)


class GoBackButton(ctk.CTkButton):
    def __init__(self, master: DisplayCombFrame | CombinerFrame, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.configure(text='<',
                        command=self.go_back,
                        width=15,
                        height=15,
                        corner_radius=15,
                        fg_color='purple')

    def go_back(self):
        direct_master = self.master
        subjects = direct_master.subjects
        if isinstance(direct_master, DisplayCombFrame):
            direct_master.master.current_frame = CombinerFrame(direct_master.master, subjects)
        elif isinstance(direct_master, CombinerFrame):
            direct_master.master.current_frame = MainFrame(direct_master.master, subjects)
        else:
            raise ValueError('Misplaced go back button')


class CTkSchedule(CTkTable):
    def __init__(self, master, schedule : scheduler.Schedule, **kwargs):
        headers = ['HORA'] + [i for i in schedule.columns]
        table_values = [headers] + schedule.reset_index().values.tolist()
        super().__init__(master, header_color='lightgreen', values=table_values, **kwargs)
        self.schedule = schedule
        self.apply_format()

    def apply_format(self):
        # index column
        for i in range(len(self.values)):
            self.frame[i, 0].configure(fg_color='lightgreen')

        # inner values
        default_colors = [self.fg_color, self.fg_color2]
        for i in range(1, len(self.values)):
            for j in range(1, len(self.values[0])):
                value = self.values[i][j]
                color = self.schedule.color_dict.get(value, default_colors[i%2]) # default color defined by phase
                self.frame[i, j].configure(fg_color=color)


class ScheduleTabView(ctk.CTkTabview):
    def __init__(self, master, schedules: List[scheduler.Schedule], **kwargs):
        super().__init__(master, **kwargs)
        self.schedules = schedules
        for index, schedule in enumerate(schedules):
            new_name = f"Comb. {index + 1}"
            self.add(new_name)
            new_sched = CTkSchedule(master=self.tab(new_name), schedule=schedule)
            new_sched.grid(row=0, column=0, sticky='nsew')

def main():
    root = MainWindow()
    root.mainloop()


if __name__ == '__main__':
    main()