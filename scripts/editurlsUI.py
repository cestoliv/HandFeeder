import tkinter
import urls
import tools
import localFluxs

from tkinter import *
from tkinter import tix
import sys
import random
import webbrowser


class MainWindow(tkinter.Toplevel):


    def __init__(self, main):
        self.master = main

        self.colors = {}
        self.colors["background"] = "#1a1a1a",
        self.colors["text"] = "#ffffff"
        self.colors["btnBg"] = "#00b4c4"
        self.colors["tickColor"] = "#00b4c4"
        self.colors["btnFg"] = "#ffffff"
        self.colors["errorMsg"] = "#FF3333"

        self.initUI()

    def initUI(self):
        self.master.config(width="500", height="400")
        self.master.tk.call('wm', 'iconphoto', self.master._w, PhotoImage(file='../res/imgs/icon.png'))
        self.master.resizable(False, False)
        self.master.title('Feeds - HandFeeder')

        # Canvas principal
        self.master.configure(background = self.colors["background"])

        # Canvas liste d'url
        self.globalcan = tkinter.Canvas(self.master)
        # Canvas secondaire de la liste
        self.win = tkinter.Canvas(self.globalcan, width=150, height=80)
        self.win.grid_propagate(0)
        self.win.grid(row=0, column=0, sticky='nswe')
        self.win.config(
            bg=self.colors["background"]
        )
        # scrollbars(list)
        hScroll = Scrollbar(self.globalcan, orient=HORIZONTAL, command=self.win.xview)
        hScroll.grid(row=1, column=0, sticky='we')
        vScroll = Scrollbar(self.globalcan, orient=VERTICAL, command=self.win.yview)
        vScroll.grid(row=0, column=1, sticky='ns')
        self.win.configure(xscrollcommand=hScroll.set, yscrollcommand=vScroll.set)


        # Création de la fenetre list
        self.inFrame = self.update()
        self.win.create_window(0, 0, window=self.inFrame, anchor=NW)
        self.globalcan.place(x=15, y=140)
        # Le scroll
        self.win.configure(scrollregion=self.win.bbox(ALL))


        # Les autres éléments
        # Ajouter url
        self.add_label = tkinter.Label(self.master, 
            text="Add feed URL :",
            font = "OpenSans 16 bold",
            fg=self.colors["text"],
            bg=self.colors["background"])
        self.add_label.place(x=15,y=15)

        # L'entrée de texte
        self.addurl_entry = tkinter.Entry(self.master,
            font = "OpenSans 12 bold",
            fg=self.colors["text"],
            bg=self.colors["background"])
        self.addurl_entry.place(x=15, y=50, width=400)

        # Le boutton pour ajout url
        self.addurl_button = tkinter.Button(self.master, 
            text = "Add", 
            font = "OpenSans 13 bold",
            fg = self.colors["btnFg"],
            bg = self.colors["btnBg"],
            highlightbackground=self.colors["btnBg"],
            highlightcolor=self.colors["btnBg"],
            borderwidth=0,
            activebackground=self.colors["btnBg"],
            command= lambda: self.addUrl(self.addurl_entry.get())
        )
        self.addurl_button.place(x=430, y=48, width=50, height=30)

        # Message erreur temporaire
        self.error_label = tkinter.Label(self.master, 
            text="",
            font = "OpenSans 11 bold",
            fg=self.colors["errorMsg"],
            bg=self.colors["background"]
        )
        self.error_label.place(x=15,y=75)

        # Retirer une url
        self.remove_label = tkinter.Label(self.master, 
            text="Remove feed(s) :",
            font = "OpenSans 16 bold",
            fg=self.colors["text"],
            bg=self.colors["background"]
        )
        self.remove_label.place(x=15,y=100)

        # Boutton actualiser
        self.reload_button = tkinter.Button(self.master, 
            text="Remove", 
            command= lambda: self.removeUrl(),
            font = "OpenSans 13 bold",
            fg=self.colors["text"],
            bg=self.colors["background"],
            highlightbackground=self.colors["btnBg"],
            highlightcolor=self.colors["btnBg"],
            borderwidth=0,
            activebackground=self.colors["btnBg"]
        )
        self.reload_button.place(x=15,y=350)

        # Boutton reset
        self.reset_button = tkinter.Button(self.master, 
            text="Defaults values", 
            command= lambda: self.resetUrl(),
            font = "OpenSans 13 bold",
            fg=self.colors["text"],
            bg=self.colors["background"],
            highlightbackground=self.colors["btnBg"],
            highlightcolor=self.colors["btnBg"],
            borderwidth=0,
            activebackground=self.colors["btnBg"]
        )
        self.reset_button.place(x=130, y=350)


    def addUrl(self, url):
        listeurl = urls.getUrls()
        if (not(url in listeurl)):
            if len(url)==0:
                return
            returnCodeAdd = urls.addUrl(url)

            if returnCodeAdd == 24:
                self.error_label.config(text="Format error (https://...)")
            else:
                self.error_label.config(text="")
                lenght = len(url)+1
                self.addurl_entry.delete(0,lenght)
                self.actualize()
        else:
            lenght = len(url)+1
            self.addurl_entry.delete(0,lenght)
            return


    def removeUrl(self):
        url = urls.getUrls()
        for i in range(len(url)):
            var = globals()['var_checkbutton_'+str(i)].get()
            if (var == 1):
                url_to_remove = url[i]
                urls.removeUrl(url_to_remove)
        self.actualize()


    def resetUrl(self):
        urls.resetFile()
        self.actualize()


    def actualize(self):

        self.inFrame.destroy()
        self.inFrame = self.update()
        self.win.create_window(0, 0, window=self.inFrame, anchor=NW)

        # scroll
        self.win.configure(scrollregion=self.win.bbox(ALL))


    def update(self):
        inFrame = tkinter.Frame(self.win)
        inFrame.config(
            bg=self.colors["background"]
        )
        self.url = urls.getUrls()

        # Définition des variables des checkbuttons
        for i in range(len(self.url)):
            globals()['var_checkbutton_'+str(i)] = tkinter.IntVar()


        id = 0
        for i in self.url:
            url = tools.domainOfUrl(i)
            if url != "" :
                simple_frame = tkinter.Frame(inFrame,
                    bg=self.colors["background"]
                )
                f = tkinter.IntVar(value=0)
                globals()['checkbutton_'+str(id)] = tkinter.Checkbutton(simple_frame, 
                    variable=globals()['var_checkbutton_'+str(id)],
                    fg=self.colors["tickColor"],
                    bg=self.colors["background"],
                    highlightbackground=self.colors["background"],
                    selectcolor=self.colors["text"],
                    highlightcolor=self.colors["background"],
                    activebackground=self.colors["background"],
                    activeforeground=self.colors["background"],
                    borderwidth=0
                )
                globals()['checkbutton_'+str(id)].pack(side="left")

                label = tkinter.Label(simple_frame, 
                    text=url,
                    font = "OpenSans 11 bold",
                    fg=self.colors["text"],
                    bg=self.colors["background"]
                )
                label.pack()
                simple_frame.pack(padx=1, pady=2,anchor='w')
            id += 1

        inFrame.pack()

        inFrame.update()
        self.win.configure(width=450, height=180)

        return inFrame


#root = Tk()
#root.config(bg="#1a1a1a")
#topEditUrl = Toplevel()
#app = MainWindow(topEditUrl)
#root.mainloop()