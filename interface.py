from tkinter import filedialog
from tkinter import *
from tkinter.ttk import *
import tktooltip as tktip
import threading
import ocr
import time
import os

class ConfigData():
    def __init__(self):
        self.entree_path = "C:/Users/smban/Downloads/Scan"
        self.sortie_path = "C:/Users/smban/Downloads/Cours"
        self.fichier_path = ""
        self.selection_type = 0
        self.rename_type = 2
        self.move_type = 0
        self.analyse_type = 2
        self.bdd_entry = 1
        self.full_logs = 0
        self.is_running = False
        self.main_window = Window(self)
    def ShowDatas(self):
        print(self.entree_path)
        print(self.sortie_path)
        print(self.fichier_path)
        print(self.selection_type)
        print(self.rename_type)
        print(self.move_type)
        print(self.analyse_type)
        print(self.bdd_entry)
    def StartStop(self):
        if self.is_running:
            self.is_running = False
            self.main_window.UpdateStartButton()
            self.main_window.AddToLog("\nSystème mis en pause. En attente d'un redémarrage...")
        else:
            if self.selection_type == 1:
                if os.path.exists(self.fichier_path):
                    self.is_running = True
                    if self.analyse_type == 3:
                        self.main_window.CorrectionWindow(self.fichier_path, {"relative_to" : "Inconnu","grade" : "Inconnu","matiere" : "Inconnu","chapter" : "Inconnu","cours_type" : "Inconnu","number" : "Inconnu","doc_type" : "Inconnu"})
                    else:
                        ocr_thread = threading.Thread(target=ocr.ScanFile, args=(self, self.fichier_path,self.full_logs))
                        ocr_thread.start()
                    self.main_window.UpdateStartButton()
                else:
                    self.main_window.SendError(404)
            else:
                self.is_running = True
                self.main_window.UpdateStartButton()
                if not ocr.is_scanning:
                    self.NextScan()

    def NextScan(self):
        scanfile = None
        for file in os.listdir(self.entree_path):
            if file.endswith(".pdf"):
                scanfile = os.path.join(self.entree_path, file)
        if scanfile != None:
            #print(scanfile)
            if self.analyse_type == 3:
                self.main_window.CorrectionWindow(self.fichier_path, {"relative_to" : "Inconnu","grade" : "Inconnu","matiere" : "Inconnu","chapter" : "Inconnu","cours_type" : "Inconnu","number" : "Inconnu","doc_type" : "Inconnu"})
            else:
                ocr_thread = threading.Thread(target=ocr.ScanFile, args=(self, scanfile,self.full_logs))
                ocr_thread.start()
        else:
            self.main_window.status_label.configure(text="En attente d'un fichier à scanner dans le dossier d'entrée...")


class Window():
    def __init__(self, master):
        self.data = master

        self.fenetre = Tk()
        #self.fenetre.geometry("600x840")
        #self.fenetre.title("OCR File Sorter")

        self.Radiobuttonsgroups = [
            {"variable" : IntVar(), "text": "Choix de sélection des fichiers :", "default" : self.data.selection_type, "buttons" : [("Sélection automatique", "Tous les fichiers sont traités automatiquement dès qu'ils sont ajoutés au dossier d'entée"), ("Sélection manuelle", "Seul le fichier sélectionné sera traité")]},
            {"variable" : IntVar(), "text": "Renommer avec :", "default" : self.data.rename_type, "buttons" : [("Code brut", "Le fichier sera renommé avec le code brut détecté par l'OCR"), ("Code final analysé", "Le fichier sera renommé avec le code analysé et traité"), ("Phrase descriptive", "Le fichier sera renommé avec le code analysé transcrit en mots français formant une phrase compréhensible"), ("Ne pas renommer", "Le fichier ne sera pas renommé")]},
            {"variable" : IntVar(), "text": "Déplacer et trier le fichier:", "default" : self.data.move_type, "buttons" : [("Systématiquement", "Le fichier sera déplacé et trier dans les sous-dossiers du dossier de sortie en fonction de son code analysé"), ("Si code correct", "Le fichier sera trié si le code a pu être analysé correctement, sinon il sera déplacé dans le dossier de sortie sans être trié"), ("Déplacer sans trier", "Le fichier sera déplacé dans le dossier de sortie sans être trié dans les sous-dossiers"), ("Ne pas déplacer", "Le fichier ne sera pas déplacé")]},
            {"variable" : IntVar(), "text": "Analyser le code :", "default" : self.data.analyse_type, "buttons" : [("Automatiquement sans confirmation", "Le fichier est analysé, renommé, déplacé et trié automatiquement sans aucune intérruption, même si l'analyse échoue"), ("Avec correction si nécessaire", "En cas d'erreur d'analyse, les informations manquantes devront être complétées autoamtiquement"), ("Automatiquement avec confirmation", "L'analyse doit être confirmée manuellement (avec modification possible) avant de renommer, déplacer et trier le fichier"), ("Manuellement", "Toutes les informations doivent être entrées manuellement et le fichier ne sera pas analysé")]}
        ]

        Label(self.fenetre, text="Dossier d'entrée :").grid(row=0, column=0, padx=3, pady=4)
        Label(self.fenetre, text="Dossier de sortie :").grid(row=1, column=0, padx=3, pady=4)
        Label(self.fenetre, text="Fichier à analyser :").grid(row=2, column=0, padx=3, pady=4)

        self.entry_entree = Entry(self.fenetre)
        self.entry_entree.insert(0, self.data.entree_path)
        self.entry_entree.grid(row=0, column=1, ipadx=100)

        self.entry_sortie = Entry(self.fenetre)
        self.entry_sortie.insert(0, self.data.sortie_path)
        self.entry_sortie.grid(row=1, column=1, ipadx=100)

        self.entry_fichier = Entry(self.fenetre)
        self.entry_fichier.grid(row=2, column=1, ipadx=100)

        self.entree_path_selector = Button(self.fenetre, text="Sélectionner", command=self._browse_entree_folder)
        self.entree_path_selector.grid(row=0, column=2, padx=5, pady=3)

        self.entree_path_selector = Button(self.fenetre, text="Sélectionner", command=self._browse_sortie_folder)
        self.entree_path_selector.grid(row=1, column=2, padx=5)

        self.fichier_path_selector = Button(self.fenetre, text="Sélectionner", command=self._browse_fichier_file)
        self.fichier_path_selector.grid(row=2, column=2, padx=5, pady=3)

        self.path_validate = Button(self.fenetre, text="Valider", command=self._validate_path)
        self.path_validate.grid(row=0, column=3, rowspan = 3, ipady=25)

        Separator(self.fenetre, orient=HORIZONTAL).grid(row=3, columnspan=4, sticky="ew", pady=5)

        row_global = 4
        for cur_group in self.Radiobuttonsgroups:
            #Style().configure("Modif.TLabelFrame", borderwidth=10)
            group = LabelFrame(self.fenetre, text = cur_group["text"])
            group.grid(row=row_global, column=0, columnspan=2, sticky="w", padx=10, pady=5)
            row = 0
            cur_group["variable"].set(cur_group["default"])
            for cur_index in range(len(cur_group["buttons"])):
                rb = Radiobutton(group, text=cur_group["buttons"][cur_index][0], variable=cur_group["variable"], value=cur_index, command=self._UpdateRadioButtons)
                rb.grid(row=row, column=0, sticky="w", padx=5)
                tktip.CreateToolTip(rb, cur_group["buttons"][cur_index][1])
                row += 1
            row_global += 1

        self.bdd_entry_checkbox_value = IntVar()
        self.bdd_entry_checkbox_value.set(self.data.bdd_entry)
        self.bdd_entry_checkbox = Checkbutton(self.fenetre, text="Ajouter les informations à la base de donnée", var=self.bdd_entry_checkbox_value, command=self._UpdateRadioButtons)
        self.bdd_entry_checkbox.grid(row=8, columnspan=4, padx=8, pady=(5,0), sticky="w")

        self.full_logs_checkbox_value = IntVar()
        self.full_logs_checkbox_value.set(self.data.full_logs)
        self.full_logs_checkbox = Checkbutton(self.fenetre, text="Afficher les logs complets", var=self.full_logs_checkbox_value, command=self._UpdateRadioButtons)
        self.full_logs_checkbox.grid(row=9, columnspan=4, padx=8, pady=(0,5), sticky="w")

        Separator(self.fenetre, orient=HORIZONTAL).grid(row=10, columnspan=4, sticky="ew")

        self.status_label = Label(self.fenetre, text = "Statut :")
        self.status_label.grid(row=11, columnspan=3, sticky="w", padx=10, pady=7)

        self.start_button = Button(self.fenetre, text="Démarrer", command=self.data.StartStop)
        self.start_button.grid(row=11, column=3, sticky="e")

        self.progress_bar = Progressbar(self.fenetre, orient = HORIZONTAL, mode = 'determinate')
        self.progress_bar.grid(row=12, columnspan=4, ipadx=215, ipady=3, sticky="w", padx=20)
        self.progress_bar["value"] = 0

        self.progress_label = Label(self.fenetre, text = "0%")
        self.progress_label.grid(row=12, column=3, sticky="e", padx=3)

        self.log_scrollbar = Scrollbar(self.fenetre)
        self.log_scrollbar.grid(row=13, column=3, sticky="e", ipady=50)

        self.log_text = Text(self.fenetre, width=70, height=10, yscrollcommand=self.log_scrollbar.set, state="disabled")
        self.log_text.grid(row=13, columnspan=4, sticky="w", padx=10, pady=(20, 5))
        self.log_scrollbar.config(command=self.log_text.yview)

        self.auto_scroll_checkbox_value = IntVar()
        self.auto_scroll_checkbox_value.set(1)
        self.auto_scroll_checkbox = Checkbutton(self.fenetre, text="Défilement automatique", var=self.auto_scroll_checkbox_value)
        self.auto_scroll_checkbox.grid(row=14, columnspan=4, padx=8, sticky="w")

        self.AddToLog("\nSystème initialisé avec succès ! En attente du démarrage")

    def StartMainLoop(self):
        self.UpdateStartButton()
        self.MainLoop()
        self.fenetre.mainloop()

    def MainLoop(self):
        self.AddToLog(ocr.GetLogs())
        if self.data.is_running:
            if ocr.is_scanning:
                if ocr.open_correction_window == True:
                    ocr.open_correction_window = False
                    self.CorrectionWindow(ocr.file, ocr.final_result)
                self._UpdateProgressBar()
                self.status_label.configure(text="Statut : Traitement de '{}' en cours... ({}/{})".format(os.path.basename(ocr.file), ocr.thresh, ocr.max_thresh))
            else:
                self.progress_bar["value"] = 0
                self.progress_label.configure(text="0%")
                if self.data.selection_type == 0:
                    self.data.NextScan()
        self.fenetre.after(10, self.MainLoop)

    def UpdateStartButton(self):
        if self.data.is_running:
            self.start_button.configure(text="Arrêter")
        else:
            self.start_button.configure(text="Démarrer")
            self.status_label.configure(text="Statut : En pause. En attente de démarrage...")

    def SendError(self, code):
        if code == 404:
            self.status_label.configure(text = "Statut : Erreur : Fichier spécifié inexistant !")
            self.AddToLog("\nErreur : Le fichier spécifié pour l'analyse n'existe pas ! Sélectionnez un autre fichier et réessayez...")

    def _UpdateProgressBar(self):
        percent = (ocr.thresh-ocr.start_thresh)/(ocr.max_thresh-ocr.start_thresh)*100
        self.progress_bar["value"] = percent
        self.progress_label.configure(text=str(min(round(percent,1), 100))+"%")

    def AddToLog(self, text):
        self.log_text.config(state="normal")
        self.log_text.insert(END, text)
        self.log_text.config(state="disabled")
        if self.auto_scroll_checkbox_value.get() == 1:
            self.log_text.see("end")

    def _UpdateRadioButtons(self):
        self.data.selection_type = self.Radiobuttonsgroups[0]["variable"].get()
        self.data.rename_type = self.Radiobuttonsgroups[1]["variable"].get()
        self.data.move_type = self.Radiobuttonsgroups[2]["variable"].get()
        self.data.analyse_type = self.Radiobuttonsgroups[3]["variable"].get()
        self.data.bdd_entry = self.bdd_entry_checkbox_value.get()
        if self.full_logs_checkbox_value.get() == 1:
            self.data.full_logs = True
        else:
            self.data.full_logs = False
        self.AddToLog("\nConfiguration modifiée avec succès")
        #self.data.ShowDatas()

    def _browse_entree_folder(self):
        output_folder = filedialog.askdirectory(parent=self.fenetre, initialdir=self.entry_entree.get(), title="Sélectionner le dossier d'entrée")
        if output_folder != "":
            self.entry_entree.delete(0, END)
            self.entry_entree.insert(0, output_folder)
            self.AddToLog("\nNouveau répertoire d'entrée sélectionné : "+output_folder)

    def _browse_sortie_folder(self):
        output_folder = filedialog.askdirectory(parent=self.fenetre, initialdir=self.entry_sortie.get(), title="Sélectionner le dossier de sortie")
        if output_folder != "":
            self.AddToLog("\nNouveau répertoire de sortie sélectionné : "+output_folder)
            self.entry_sortie.delete(0, END)
            self.entry_sortie.insert(0, output_folder)

    def _browse_fichier_file(self):
        output_folder = filedialog.askopenfilename(parent=self.fenetre, initialdir=self.entry_entree.get(), title="Sélectionner le fichier à analyser")
        self.entry_fichier.delete(0, END)
        self.entry_fichier.insert(0, output_folder)
        self.AddToLog("\nNouveau fichier à analysé sélectionné : "+output_folder)

    def _validate_path(self):
        self.data.entree_path = self.entry_entree.get()
        self.data.sortie_path = self.entry_sortie.get()
        self.data.fichier_path = self.entry_fichier.get()
        Style().configure("Modif.TButton", foreground="green")
        self.path_validate.configure(text = "Modifié !", style = "Modif.TButton")
        self.path_validate.after(2000, self._refresh_path_validate_button)
        #self.data.ShowDatas()
        self.AddToLog("\nRépertoires et fichiers sélectionnés enregistrés !")

    def _refresh_path_validate_button(self):
        self.path_validate.configure(text = "Valider", style = "TButton")

    def CorrectionWindow(self, file, results):
        self.correction = Toplevel(self.fenetre)
        self.results = results
        self.file = file

        Label(self.correction, text = "Correction et demande de confirmation du fichier ""{}""".format(file)).grid(row = 0, column=0, columnspan=2)

        Button(self.correction, text = "Ouvrir le fichier", command=self.OpenFile).grid(row = 1, column=0, columnspan=2)

        Label(self.correction, text="Document relatif à :").grid(row=2, column=0, padx=3, pady=4, sticky=E)
        Label(self.correction, text="Année/Classe du document :").grid(row=3, column=0, padx=3, pady=4, sticky=E)
        Label(self.correction, text="Matière du document :").grid(row=4, column=0, padx=3, pady=4, sticky=E)
        Label(self.correction, text="Chapitre du document :").grid(row=5, column=0, padx=3, pady=4, sticky=E)
        Label(self.correction, text="Type de cours :").grid(row=6, column=0, padx=3, pady=4, sticky=E)
        Label(self.correction, text="Numéro du document :").grid(row=7, column=0, padx=3, pady=4, sticky=E)
        Label(self.correction, text="Type de document :").grid(row=8, column=0, padx=3, pady=4, sticky=E)
        Label(self.correction, text="Numéro de page :").grid(row=9, column=0, padx=3, pady=4, sticky=E)
        Label(self.correction, text="Date du document :").grid(row=10, column=0, padx=3, pady=4, sticky=E)

        self.correction_listboxs = [
        {"row" : 2, "variable" : StringVar(self.correction), "default" : 1, "index" : "relative_to", "listbox" : None,"texts" : ["Cours", "Divers"]},
        {"row" : 3, "variable" : StringVar(self.correction), "default" : 1, "index" : "grade", "listbox" : None,"texts" : ["MPSI", "MP"]},
        {"row" : 4, "variable" : StringVar(self.correction), "default" : 2, "index" : "matiere", "listbox" : None,"texts" : ["Français","Maths", "Physique"]},
        {"row" : 6, "variable" : StringVar(self.correction), "default" : 2, "index" : "cours_type", "listbox" : None,"texts" : ["Cours", "Exercice", "Travaux pratiques", "Travaux Dirigés", "Devoir surveillé"]},
        {"row" : 8, "variable" : StringVar(self.correction), "default" : 3, "index" : "doc_type", "listbox" : None,"texts" : ["Ennoncé", "Brouillon", "Réponse", "Corrigé"]}]

        for cur_listbox in self.correction_listboxs:
            options = cur_listbox["texts"]
            options.insert(0,"Inconnu")
            if self.Radiobuttonsgroups[3]["variable"].get() == 3:
                cur_listbox["variable"].set(options[cur_listbox["default"]])
            elif self.results[cur_listbox["index"]] == "Inconnu" or self.results[cur_listbox["index"]] == "Non trouvé":
                cur_listbox["variable"].set(options[0])
            else:
                cur_listbox["variable"].set(self.results[cur_listbox["index"]])
            #cur_listbox["variable"].set("Cours")
            self.correction_listboxs[self.correction_listboxs.index(cur_listbox)]["listbox"] = OptionMenu(self.correction, cur_listbox["variable"], cur_listbox["variable"].get(), *options)
            self.correction_listboxs[self.correction_listboxs.index(cur_listbox)]["listbox"].grid(row=cur_listbox["row"], column=1, sticky=W)

        self.correction_chapitre_entry = Entry(self.correction)
        self.correction_chapitre_entry.grid(row=5, column=1, sticky=W)
        if not (self.results["chapter"] == "Inconnu" or self.results["chapter"] == "Non trouvé"):
            self.correction_chapitre_entry.insert(0, self.results["chapter"].split()[1])

        self.correction_number_entry = Entry(self.correction)
        self.correction_number_entry.grid(row=7, column=1, sticky=W)
        if not (self.results["number"] == "Inconnu" or self.results["number"] == "Non trouvé"):
            self.correction_number_entry.insert(0, self.results["number"])

        self.correction_page_entry = Entry(self.correction)
        self.correction_page_entry.grid(row=9, column=1, sticky=W)
        if "Page" in self.results.keys():
            self.correction_page_entry.insert(0, self.results["Page"])

        self.correction_date_entry = Entry(self.correction)
        self.correction_date_entry.grid(row=10, column=1, sticky=W)
        if "Date" in self.results.keys():
            self.correction_date_entry.insert(0, self.results["Date"])

        self.correction_validate_button = Button(self.correction, text="Valider", command=self.ValidateCorrection)
        self.correction_validate_button.grid(row=11, column=0, columnspan=2)
        #self.correction.mainloop()

    def ValidateCorrection(self):
        for cur_listbox in self.correction_listboxs:
            self.results[cur_listbox["index"]] = self.correction_listboxs[self.correction_listboxs.index(cur_listbox)]["variable"].get()
        if self.correction_chapitre_entry.get() != "":
            self.results["chapter"] = "Chapitre "+ self.correction_chapitre_entry.get()
        else:
            self.results["chapter"] = "Inconnu"
        if self.correction_number_entry.get() != "":
            self.results["number"] = self.correction_number_entry.get()
        else:
            self.results["number"] = "Inconnu"
        if self.correction_page_entry.get() != "":
            self.results["Page"] = self.correction_page_entry.get()
        else:
            self.results["Page"] = "Inconnu"
        if self.correction_date_entry.get() != "":
            self.results["Date"] = self.correction_date_entry.get()
        else:
            self.results["Date"] = "Inconnu"
        ocr.SortFile(self.data, self.file, self.results)
        self.correction.destroy()

    def OpenFile(self):
        os.system('"{}"'.format(ocr.file))

App = ConfigData()
App.main_window.StartMainLoop()
