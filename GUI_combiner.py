import customtkinter as ctk
from PIL import Image
import webbrowser

# Default appearance mode
ctk.set_appearance_mode('light')

# IMPORTANT CONSTANTS
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
COMBINER_BUTTON_TEXT = 'Combinador de horarios Psico UBA'

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
                                             text=COMBINER_BUTTON_TEXT,
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
        # Top Frame
        self.topFrame = ctk.CTkFrame(master=self, fg_color='transparent')
        self.topFrame.pack(expand=True, fill=ctk.X)
        self.topFrame.columnconfigure(0, weight=1)
        self.topFrame.columnconfigure(1, weight=9)

        # Go Back Button

        self.goBack = ctk.CTkButton(self.topFrame, text='<', command=self.go_back_to_main_frame,
                                    width=15, height=15, corner_radius=15)
        self.goBack.grid(row=0, column=1, sticky='w', padx=5, pady=5)

    def go_back_to_main_frame(self):
        """
        This method will be accessed from within the inputs frame
        """
        self.master.current_frame = MainFrame(self.master)



def main():
    root = MainWindow()
    root.mainloop()


if __name__ == '__main__':
    main()