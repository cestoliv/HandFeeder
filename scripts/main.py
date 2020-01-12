#encoding: utf-8
from tkinter import *
from tkinter.ttk import Progressbar, Style
from tkinter import tix
from PIL import Image, ImageFont, ImageDraw, ImageTk, ImageOps
from threading import Thread
import queue
import sys
import random
import webbrowser
import time

import localFluxs
import urls
import tools
import editurlsUI

class Entrie:
    def __init__(self, domain, name, link, summary, date, enclosure):
        self.name = name
        self.link = link
        self.date = tools.dateFromString(date)
        self.enclosure = enclosure
        self.dateString = "Le " + str(self.date.day) + " " + tools.numberToMonth(self.date.month) + " " + str(self.date.year) + " à " + str(self.date.hour) + "h" + str(self.date.minute)
        self.summary = summary[ 0 : 0 + 300]
        self.summary = self.summary.replace("\n", "")
        if self.summary == "":
            self.summary = "Pas de description..."
        self.enclosurePath = '../datas/fluxs/' + domain + "/" + self.enclosure

    def click(self, event):
        openBrowser(self.link)

class MainWindow(Canvas):
    def __init__(self):
        super().__init__()
        self.entries = localFluxs.getListOfEntries()

        #self.window_W = root.winfo_screenwidth() // problem with two screen on xfce
        self.window_W = 1080
        #self.window_Y = root.winfo_screenheight()
        self.window_Y = 720

        self.colors = {}
        self.colors["background"] = "#1a1a1a",
        self.colors["newsTitle"] = "#ffffff"
        self.colors["entrieTitle"] = "#ffffff"
        self.colors["entrieInfos"] = "#808080"
        self.colors["entrieBorder"] = "#00b4c4"
        self.colors["menuBackground"] = "#2e2e2e",
        self.colors["menuActiveBackground"] = "#1a1a1a",
        self.colors["menuForeground"] = "#ffffff",
        self.colors["menuActiveForeground"] = "#00b4c4"
        self.colors["progBarBG"] = "#ffffff"
        self.colors["progBarFG"] = "#00b4c4"

        self.scrollCount = 0
        self.initUI()

    def secondaire(self):
        topEditUrl = Toplevel()
        editurlsUI.MainWindow(topEditUrl)

    def initUI(self):
        self.master.tk.call('wm', 'iconphoto', self.master._w, PhotoImage(file='../res/imgs/icon.png'))
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.title('HandFeeder')

        ###### MENU
        menubar = Menu(self.master,
            font = "OpenSans 13 bold",
            background=self.colors["menuBackground"],
            activebackground=self.colors["menuActiveBackground"],
            foreground=self.colors["menuForeground"],
            activeforeground=self.colors["menuActiveForeground"]
        )
        self.master.config(menu=menubar)

        feedsMenu = Menu(menubar,
            font = "OpenSans 13 bold",
            background=self.colors["menuBackground"],
            activebackground=self.colors["menuActiveBackground"],
            foreground=self.colors["menuForeground"],
            activeforeground=self.colors["menuActiveForeground"]
        )
        feedsMenu.add_command(label="Actualize", command=self.actualize)
        feedsMenu.add_command(label="Feeds...", command=self.secondaire)
        menubar.add_cascade(label="Settings", menu=feedsMenu)
        ###### END MENU

        # Canvas qui fait "cadre"
        self.win = Canvas(self.master, 
            width = self.window_W, 
            height = self.window_Y, 
            background = self.colors["background"],
            highlightbackground = self.colors["background"],
            highlightcolor = self.colors["background"]
        )
        self.win.grid(row=0, column=0, sticky='nswe')
        # Scroll
        self.win.bind_all("<MouseWheel>", self.on_mousewheel) # WINDOWS
        self.win.bind_all('<4>', self.on_mousewheel) # LINUX
        self.win.bind_all('<5>', self.on_mousewheel) # LINUX

        # scrollbars
        hScroll = Scrollbar(self.master, orient=HORIZONTAL, command=self.win.xview)
        hScroll.grid(row=1, column=0, sticky='we')

        vScroll = Scrollbar(self.master, orient=VERTICAL, command=self.win.yview)
        vScroll.grid(row=0, column=1, sticky='ns')

        self.win.configure(xscrollcommand=hScroll.set, yscrollcommand=vScroll.set)

        # frame des entrées
        self.entriesFrame = self.updateEntries()

        # création de la window dans le canvas
        self.win.create_window(0, 0, window=self.entriesFrame, anchor=NW)

        # scrollregion sur toute la taille du canvas
        self.win.configure(scrollregion=self.win.bbox(ALL))

        #resize
        self.win.bind('<Configure>', self.resize)

    def resize(self, event):
        w,h = event.width, event.height

        self.win.config(width=w, height=h)
        self.window_W=w
        self.window_Y=h

        self.entriesFrame.destroy()
        self.entriesFrame = self.updateEntries()
        self.win.create_window(0, 0, window=self.entriesFrame, anchor=NW)

        # scrollregion sur toute la taille du canvas
        self.win.configure(scrollregion=self.win.bbox(ALL))        

    def actualize(self):
        # show loading animation
        self.loadingAnimation()
        # start thread for updating
        self.queue = queue.Queue()
        UpdateThread(self.queue).start()
        # check if actualize finished
        self.master.after(100, self.isActualizeFinished)

    def loadingAnimation(self):
        self.entriesFrame.destroy()
        self.entriesFrame = Frame(
            self.win, 
            bg=self.colors["background"]
        )
        Label(self.entriesFrame, bg=self.colors["background"]).pack() # For space
        news_title = Label(self.entriesFrame,
            text = "Loading...",
            font = "OpenSans 25 bold",
            fg=self.colors["newsTitle"],
            bg=self.colors["background"])
        news_title.pack(padx=80)
        Label(self.entriesFrame, bg=self.colors["background"]).pack() # For space

        barStyle = Style()
        barStyle.configure("bar.Horizontal.TProgressbar", 
            troughcolor=self.colors["progBarBG"],
            bordercolor=self.colors["progBarBG"],
            background=self.colors["progBarFG"],
            lightcolor=self.colors["progBarFG"],
            darkcolor=self.colors["progBarFG"]
        )
        self.prog_bar = Progressbar(
            self.entriesFrame, 
            style="bar.Horizontal.TProgressbar",
            orient="horizontal",
            length=200, 
            mode="indeterminate"
        )
        self.prog_bar.pack(padx=80)
        self.prog_bar.start()

        self.entriesFrame.update()
        self.win.create_window(0, 0, window=self.entriesFrame, anchor=NW)
        self.win.configure(scrollregion=self.win.bbox(ALL))
    
    def isActualizeFinished(self):
        try:
            # except if not finished
            msg = self.queue.get(0)

            # print new entries
            self.entriesFrame.destroy()
            self.entries = localFluxs.getListOfEntries()
            self.entriesFrame = self.updateEntries()
            self.win.create_window(0, 0, window=self.entriesFrame, anchor=NW)
            self.win.configure(scrollregion=self.win.bbox(ALL))
        except queue.Empty:
            # check if actualize finished
            self.master.after(100, self.isActualizeFinished)

    def updateEntries(self):
        entriesFrame = Frame(
            self.win, 
            bg=self.colors["background"]
        )

        #newsTitle
        Label(entriesFrame, bg=self.colors["background"]).pack() # For space
        news_title = Label(entriesFrame,
            text = "Latest news",
            font = "OpenSans 25 bold",
            fg=self.colors["newsTitle"],
            bg=self.colors["background"])
        news_title.pack(padx="80")
        Label(entriesFrame, bg=self.colors["background"]).pack() # For space

        # remplissage avec les articles
        for i in range(len(self.entries)):
            #Create entrie obj
            entrie = Entrie(self.entries[i]["domain"], self.entries[i]["title"], self.entries[i]["link"], self.entries[i]["summary"], self.entries[i]["date"], self.entries[i]["enclosure"])

        # Entrie frame
            entrie_frame = Frame(entriesFrame, width=self.window_W-80, height=140)
            entrie_frame.config(
                bg=self.colors["background"]
            )
            entrie_frame.bind("<Button-1>", entrie.click)

            #enclosure
            if entrie.enclosure != "":
                load = Image.open(entrie.enclosurePath)
                #load = load.thumbnail((140, 140), Image.ANTIALIAS)
                load = ImageOps.fit(load, (140, 140), Image.ANTIALIAS)
                render = ImageTk.PhotoImage(load)
                entrie_enclosure = Label(entrie_frame, 
                    image=render
                )
                entrie_enclosure.image = render
                entrie_enclosure.place(x=0, y=0)

            #title
            entrie_title = Label(entrie_frame,
                text=entrie.name,
                font = "OpenSans 18 bold",
                fg=self.colors["entrieTitle"],
                bg=self.colors["background"])
            entrie_title.bind("<Button-1>", entrie.click)
            entrie_title.place(x=160, y=15)

            #source
            entrie_source = Label(entrie_frame,
                text=tools.domainOfUrl(entrie.link),
                font = "OpenSans 15 bold",
                fg=self.colors["entrieInfos"],
                bg=self.colors["background"])
            entrie_source.bind("<Button-1>", entrie.click)
            entrie_source.place(x=160, y=45)

            #date
            entrie_date = Label(entrie_frame,
                text=entrie.dateString,
                font = "OpenSans 13 bold",
                fg=self.colors["entrieInfos"],
                bg=self.colors["background"])
            entrie_date.bind("<Button-1>", entrie.click)
            entrie_date.place(x=160, y=70)

            #summary
            entrie_desc = Label(entrie_frame,
                text=entrie.summary,
                font = "OpenSans 15 bold",
                fg=self.colors["entrieInfos"],
                bg=self.colors["background"])
            entrie_desc.bind("<Button-1>", entrie.click)
            entrie_desc.place(x=160, y=95)

            Label(entriesFrame, bg=self.colors["background"], font = "OpenSans 1 bold").pack() # For space
        # End entrie frame
            entrie_frame.pack(padx=40, pady=20)

        # calcul des dimensions
        entriesFrame.update()
        return entriesFrame

    def on_mousewheel(self, event):
        if event.num == 5 or event.delta == -120:
            self.win.yview_scroll(1, UNITS)
        if event.num == 4 or event.delta == 120:
            self.win.yview_scroll(-1, UNITS)

class UpdateThread(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
    def run(self):
        localFluxs.updateLocalFile()
        self.queue.put("Update finished")

def openBrowser(url):
    print(url)
    webbrowser.open(url)

root = Tk()
app = MainWindow()
root.mainloop()
