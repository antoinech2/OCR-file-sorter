from tkinter import filedialog
from tkinter import *
from tkinter.ttk import *
import time

class ConfigData():
    def __init__(self):
        self.entree_path = "C:/Users/smban/Downloads/Scan"
        self.sortie_path = "C:/Users/smban/Downloads/Cours"
    def ShowDatas(self):
        print(self.entree_path)
        print(self.sortie_path)

class Window():
    def __init__(self):
        self.fenetre = Tk()
        self.fenetre.geometry("590x700")

        self.Radiobuttonsgroups = [
            {"variable" : StringVar(), "position" : (5, 70), "buttons" : ["Sélection automatique", "Sélection manuelle"]}
        ]

        Label(self.fenetre, text="Dossier d'entrée :").place(x=5, y=5)
        Label(self.fenetre, text="Dossier de sortie :").place(x=5, y=30)

        self.entry_entree = Entry(self.fenetre)
        self.entry_entree.insert(0, data.entree_path)
        self.entry_entree.place(x=105, y=5, width=320)

        self.entry_sortie = Entry(self.fenetre)
        self.entry_sortie.insert(0, data.sortie_path)
        self.entry_sortie.place(x=105, y=30, width=320)

        self.entree_path_selector = Button(self.fenetre, text="Sélectionner", command=self._browse_entree_folder)
        self.entree_path_selector.place(x=430, y=3)

        self.entree_path_selector = Button(self.fenetre, text="Sélectionner", command=self._browse_sortie_folder)
        self.entree_path_selector.place(x=430, y=27)

        self.path_validate = Button(self.fenetre, text="Valider", command=self._validate_path)
        self.path_validate.place(x=510, y=13)

        Separator(self.fenetre, orient=HORIZONTAL).place(x=0, y=60, relwidth=1)

        for cur_group in self.Radiobuttonsgroups:
            group = LabelFrame(self.fenetre, text = "Test")
            group.place(x=cur_group["position"][0], y=cur_group["position"][1], width=300, height=200)
            y = 0#cur_group["position"][1]+20
            for cur_button in cur_group["buttons"]:
                Radiobutton(group, text=cur_button, variable=cur_group["variable"], value=cur_button).place(x=cur_group["position"][0]+10, y=y)
                y += 20
            #group.configure(height=50)
        self.fenetre.mainloop()

    def _browse_entree_folder(self):
        output_folder = filedialog.askdirectory(parent=self.fenetre, initialdir=self.entry_entree.get(), title="Sélectionner le dossier d'entrée")
        if output_folder != "":
            self.entry_entree.delete(0, END)
            self.entry_entree.insert(0, output_folder)

    def _browse_sortie_folder(self):
        output_folder = filedialog.askdirectory(parent=self.fenetre, initialdir=self.entry_sortie.get(), title="Sélectionner le dossier de sortie")
        if output_folder != "":
            self.entry_sortie.delete(0, END)
            self.entry_sortie.insert(0, output_folder)

    def _validate_path(self):
        data.entree_path = self.entry_entree.get()
        data.sortie_path = self.entry_sortie.get()
        Style().configure("Modif.TButton", foreground="green")
        self.path_validate.configure(text = "Modifié !", style = "Modif.TButton")
        self.path_validate.after(2000, self._refresh_path_validate_button)
        data.ShowDatas()

    def _refresh_path_validate_button(self):
        self.path_validate.configure(text = "Valider", style = "TButton")

data = ConfigData()
fenetre = Window()
