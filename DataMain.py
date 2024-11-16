import tkinter as tk
import GUI as GUI

class Main(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        master.minsize(400, 400)
        GUI.center_window(master)
        self.next = ""

        lbl = tk.Label(self, text="this is the main frame\n")
        lbl.pack()

        btn = tk.Button(self, text='Import CSV', command=self.open_popupImport)
        btn.pack()

        btn = tk.Button(self, text='Delete dateset', command=self.open_popupDelete)
        btn.pack()

        btn = tk.Button(self, text='Condense dataset/ reomve unnesacery Columns', command=self.open_popupCondense)
        btn.pack()

        btn = tk.Button(self, text='Select Specific rows from dataset', command=self.open_popupSlectRows)
        btn.pack()

        btn = tk.Button(self, text='Plot scatter graph', command=self.open_popupGraph)
        btn.pack()

        btn = tk.Button(self, text='Plot normal distribution', command=self.open_popupNormal)
        btn.pack()

        btn = tk.Button(self, text='Clean null values from data', command=self.open_popupRemoveNull)
        btn.pack()

        btn = tk.Button(self, text='Predict value with new data', command=self.open_popupPredict)
        btn.pack()

        btn = tk.Button(self, text='Find equivalent value in different data set', command=self.open_popupNormalCheck)
        btn.pack()

        self.output = tk.Label(self)
        self.output.pack()

    def open_popupImport(self):
        p = GUI.PopupLoad(self)

    def open_popupDelete(self):
        p = GUI.PopupDelete(self)

    def open_popupCondense(self):
        self.next = "Condense"
        p = GUI.PopupTableSelect(self)

    def open_popupSlectRows(self):
        self.next = "SelectRows"
        p = GUI.PopupTableSelect(self)

    def open_popupGraph(self):
        self.next = "Graph"
        p = GUI.PopupTableSelect(self)

    def open_popupPredict(self):
        self.next = "Predict"
        p = GUI.PopupTableSelect(self)

    def open_popupRemoveNull(self):
        self.next = "RemoveNull"
        p = GUI.PopupTableSelect(self)

    def open_popupNormalCheck(self):
        p = GUI.PopupNormalCheck(self)

    def open_popupNormal(self):
        self.next = "Normal"
        p = GUI.PopupSelectAnyColumns(self)

def main():
    root = tk.Tk()
    window = Main(root)
    window.pack()
    root.mainloop()

main()
