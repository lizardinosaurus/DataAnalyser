import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import *
import DBFunctions as DB
import StatFunctions as stat
import sqlite3
import os

conn = sqlite3.connect("rawdata.db")
cursor = conn.cursor()


def center_window(win):
    """
    center a tkinter window.

    :param win: the window to center
    """
    win.update()
    scr_width, scr_height = win.winfo_screenwidth(), win.winfo_screenheight()
    border_width = win.winfo_rootx() - win.winfo_x()
    title_height = win.winfo_rooty() - win.winfo_y()
    win_width = win.winfo_width() + border_width + border_width
    win_height = win.winfo_height() + title_height + border_width
    x = (scr_width - win_width) // 2
    y = (scr_height - win_height) // 2
    win.geometry("+%d+%d" % (x, y))

        


class PopupNormalCheck(tk.Toplevel):
    """modal window requires a master"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.minsize(500, 500)
        center_window(self)

        for i in range(10):
            self.columnconfigure(i, weight=1)

        for i in range(10):
            self.rowconfigure(i, weight=1)
        
        self.outputx = []
        self.outputy = []
        
        lbl = tk.Label(self, text="Choose the x and y axis value for the scatter\nPick one column per axis")
        lbl.grid(row = 1, column = 5)

        btn1 = tk.Button(self, text='choose set of values with data point you know', command=self.open_xpopup)
        btn1.grid(row = 2, column = 5, sticky = W+E+N+S)

        lbl = tk.Label(self, text="Enter the value you know")
        lbl.grid(row = 3, column = 5, sticky = W)

        self.ent = tk.Entry(self, width = 20)
        self.ent.grid(row = 3, column = 5, sticky = E)

        btn2 = tk.Button(self, text='choose set of values where you want to find equivalent point', command=self.open_ypopup)
        btn2.grid(row= 4, column = 5, sticky = W+E+N+S)

        btn3 = tk.Button(self, text="Find equivalent value", command=self.on_ok)
        btn3.grid(row = 5, column = 5, sticky = W+E+N+S)


        # The following commands keep the popup on top.
        # Remove these if you want a program with 2 responding windows.
        # These commands must be at the end of __init__
        self.transient(master) # set to be on top of the main window
        self.grab_set() # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self) # pause anything on the main window until this one closes

    def open_xpopup(self):
        p = PopupSelectAnyColumns(self)
        self.outputx = (p.result)
        lbl = tk.Label(self, text=self.outputx)
        lbl.grid(row = 2, column = 6)

    def open_ypopup(self):
        p = PopupSelectAnyColumns(self)
        self.outputy = (p.result)
        lbl = tk.Label(self, text=self.outputy)
        lbl.grid(row = 4, column = 6)

    def on_ok(self):
        if ((self.outputx[0] == 'None' or self.outputx == []) or (self.outputy[0] == 'None' or self.outputy == [])):
            lbl = tk.Label(self, text="Missing rows!") 
            lbl.grid(row = 6, column = 5)
        else:
            result = stat.getValueOfStandardDeviation(DB.selectColumn(self.outputy[0], self.outputy[1]), stat.getStandardDeviationsOfValue(DB.selectColumn(self.outputx[0], self.outputx[1]), float(self.ent.get())))
            lbl = tk.Label(self, text=result) 
            lbl.grid(row = 6, column = 5)


class PopupRemoveNull(tk.Toplevel):
    """modal window requires a master"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.minsize(700, 500)
        center_window(self)

        self.output = (str(master.output[0])).strip(",()\'")

        for i in range(10):
            self.columnconfigure(i, weight=1)

        for i in range(10):
            self.rowconfigure(i, weight=1)
        
        self.outputgroup = []
        self.outputsum = []
        
        lbl = tk.Label(self, text="Ccreate new table from {} with no null values".format(self.output))
        lbl.grid(row = 1, column = 5)

        lbl = tk.Label(self, text="Enter a name for the new table")
        lbl.grid(row = 3, column = 5, sticky = W)

        self.ent1 = tk.Entry(self, width = 25)
        self.ent1.grid(row = 3, column = 5, sticky = E)

        btn = tk.Button(self, text="Remove null values", command=self.on_ok)
        btn.grid(row = 4, column = 5, sticky = W+E+N+S)

        # The following commands keep the popup on top.
        # Remove these if you want a program with 2 responding windows.
        # These commands must be at the end of __init__
        self.transient(master) # set to be on top of the main window
        self.grab_set() # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self) # pause anything on the main window until this one closes


    def on_ok(self):
        DB.cleanByRemovingNull(self.output, self.ent1.get())
        self.destroy()
        

class PopupDelete(tk.Toplevel):
    """modal window requires a master"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        center_window(self)

        lbl = tk.Label(self, text="Select 1 value for the axis")
        lbl.pack()

        self.ent = []

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        checkboxes = []

        for table in tables:
            checkbox_value = table
            checkbox_var = tk.BooleanVar()
            checkbox_var.set(False)  # Set the initial state (unchecked)

            checkbox = tk.Checkbutton(self, text=checkbox_value, variable=checkbox_var)
            checkbox.pack(pady=5)
            checkbox.var = checkbox_var
            checkbox.table = table
            checkboxes.append(checkbox)


        btn = tk.Button(self, text="OK", command=lambda: self.on_ok(checkboxes))
        btn.pack()

        # The following commands keep the popup on top.
        # Remove these if you want a program with 2 responding windows.
        # These commands must be at the end of __init__
        self.transient(master) # set to be on top of the main window
        self.grab_set() # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self) # pause anything on the main window until this one closes

    def on_ok(self, checkboxes):
        count = 0
        for box in checkboxes:
            if(box.var.get()):
                count += 1
        if (count == 0):
            self.destroy()
        else:
            for box in checkboxes:
                if(box.var.get()):
                    self.ent.append(box.table)
                    DB.deleteFile(self.ent)
                    self.destroy()



class PopupTableSelect(tk.Toplevel):
    """modal window requires a master"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        center_window(self)

        self.ent = []

        self.next = master.next

        if(self.next == "Predict"):
            lbl = tk.Label(self, text="Select the table you want to use\nEnsure no null values (Use the clean function on main page)")
        else:
            lbl = tk.Label(self, text="Select the table you want to use")
        lbl.pack()


        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        checkboxes = []

        text = ScrolledText(self, width=50, height=20)
        text.pack()

        for table in tables:
            checkbox_value = table
            checkbox_var = tk.BooleanVar()
            checkbox_var.set(False)  # Set the initial state (unchecked)
            checkbox = tk.Checkbutton(text, text=checkbox_value, variable=checkbox_var, bg='white', anchor = 'w')
            text.window_create('end', window=checkbox)
            text.insert('end', '\n')
            checkbox.var = checkbox_var
            checkbox.table = table
            checkboxes.append(checkbox)


        btn = tk.Button(self, text="OK", command=lambda: self.on_ok(checkboxes))
        btn.pack()

        # The following commands keep the popup on top.
        # Remove these if you want a program with 2 responding windows.
        # These commands must be at the end of __init__
        self.transient(master) # set to be on top of the main window
        self.grab_set() # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self) # pause anything on the main window until this one closes

        self.output = ""

    def on_ok(self, checkboxes):
        count = 0
        for box in checkboxes:
            if(box.var.get()):
                count += 1
        if (count != 1):
            self.destroy()
        else:
            for box in checkboxes:
                if(box.var.get()):
                    self.ent.append(box.table)
                    self.output = self.ent
                    if (self.next == "Condense"):
                        p = PopupCondense(self)
                        self.destroy()
                        
                    if (self.next == "Predict"):
                        p = PopupPredict(self)

                    if (self.next == "RemoveNull"):
                        p = PopupRemoveNull(self)

                    if (self.next == "SelectRows"):
                        p = PopupSelectRows(self)

                    if (self.next == "Graph"):
                        p = PopupGraph(self)



class PopupSelectRows(tk.Toplevel):
    """modal window requires a master"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.minsize(500, 500)
        center_window(self)

        for i in range(10):
            self.columnconfigure(i, weight=1)

        for i in range(10):
            self.rowconfigure(i, weight=1)

        self.output = (str(master.output[0])).strip(",()\'")
        
        self.outputdata = []
        self.inputs = []
        self.columns = []
        
        lbl = tk.Label(self, text="Choose the columns that you want to enter a condition")
        lbl.grid(row = 1, column = 5)

        btn1 = tk.Button(self, text='choose condition columns', command=self.open_selectpopup)
        btn1.grid(row = 2, column = 5, sticky = W+E+N+S)

        lbl = tk.Label(self, text="Enter a name for the new table")
        lbl.grid(row = 3, column = 5, sticky = W)

        self.ent = tk.Entry(self, width = 20)
        self.ent.grid(row = 3, column = 5, sticky = E)

        btn3 = tk.Button(self, text="Next", command=self.on_ok)
        btn3.grid(row = 4, column = 5, sticky = W+E+N+S)


        # The following commands keep the popup on top.
        # Remove these if you want a program with 2 responding windows.
        # These commands must be at the end of __init__
        self.transient(master) # set to be on top of the main window
        self.grab_set() # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self) # pause anything on the main window until this one closes

    def open_selectpopup(self):
        selected = []
        p = PopupSelectColumns(self)
        self.outputdata = (p.result)
        for i in range(0, len(self.outputdata), 2):
            selected.append(self.outputdata[i])
        self.columns = selected
        lbl = tk.Label(self, text=selected)
        lbl.grid(row = 2, column = 6)

    def on_ok(self):
        if (self.outputdata == []):
            lbl = tk.Label(self, text="Invalid Selection!") 
            lbl.grid(row = 5, column = 5)
        else:
            p = PopupEnterData(self)
            self.inputs = p.result
            DB.condenseRows(self.inputs, self.columns, DB.getColumnNames(self.output), self.output, self.ent.get())

class PopupPredict(tk.Toplevel):
    """modal window requires a master"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.minsize(500, 500)
        center_window(self)

        for i in range(10):
            self.columnconfigure(i, weight=1)

        for i in range(10):
            self.rowconfigure(i, weight=1)

        self.output = (str(master.output[0])).strip(",()\'")
        
        self.outputpredict = []
        self.outputdata = []
        self.inputs = []
        
        lbl = tk.Label(self, text="Choose the columns that will be used for the prediction")
        lbl.grid(row = 1, column = 5)

        btn1 = tk.Button(self, text='select the value you want to predict', command=self.open_predictpopup)
        btn1.grid(row = 2, column = 5, sticky = W+E+N+S)

        btn2 = tk.Button(self, text='select the values you know', command=self.open_datapopup)
        btn2.grid(row= 3, column = 5, sticky = W+E+N+S)

        btn3 = tk.Button(self, text="Next", command=self.on_ok)
        btn3.grid(row = 4, column = 5, sticky = W+E+N+S)


        # The following commands keep the popup on top.
        # Remove these if you want a program with 2 responding windows.
        # These commands must be at the end of __init__
        self.transient(master) # set to be on top of the main window
        self.grab_set() # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self) # pause anything on the main window until this one closes

    def open_predictpopup(self):
        p = PopupSelectColumns(self)
        self.outputpredict = (p.result)
        for i in range(0, len(self.outputpredict), 2):
            lbl = tk.Label(self, text=self.outputpredict[i])
            lbl.grid(row = int(2+(i/2)), column = 6)

    def open_datapopup(self):
        selected = []
        p = PopupSelectColumns(self)
        self.outputdata = (p.result)
        for i in range(0, len(self.outputdata), 2):
            selected.append(self.outputdata[i])
        lbl = tk.Label(self, text=selected)
        lbl.grid(row = 3, column = 6)

    def on_ok(self):
        if ((self.outputpredict == [] or len(self.outputpredict) > 2) or (self.outputdata == [])):
            lbl = tk.Label(self, text="Invalid Selection!") 
            lbl.grid(row = 4, column = 6)
        else:
            p = PopupEnterData(self)
            self.inputs = p.result
            prediction = stat.predictValue(self.outputdata, self.output, self.outputpredict, self.inputs)
            lbl = tk.Label(self, text="For this data you would expect {} for {}".format(prediction[0], self.outputpredict[0]))
            lbl.grid(row = 5, column = 5)
            
                    
class PopupEnterData(tk.Toplevel):
    """modal window requires a master"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        center_window(self)

        table = master.output

        lbl = tk.Label(self, text="Select columns from {}".format(table))
        lbl.pack()

        self.ent = []

        entries = []

        text = ScrolledText(self, width=35, height=20)
        text.pack()

        names = master.outputdata
        for i in range(0, len(names), 2):
            if (names[i] != "rowID"):
                entry_name = names[i]
                entry_var = tk.StringVar()
                entry = tk.Entry(text, text=entry_name, textvariable=entry_var, bg='white', width = 50)
                text.window_create('end', window=entry)
                text.insert('end', '\n')
                entry.insert(0, str(names[i]))
                entry.var = entry_var
                entries.append(entry)


        btn = tk.Button(self, text="OK", command=lambda: self.on_ok(entries))
        btn.pack()

        # The following commands keep the popup on top.
        # Remove these if you want a program with 2 responding windows.
        # These commands must be at the end of __init__
        self.transient(master) # set to be on top of the main window
        self.grab_set() # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self) # pause anything on the main window until this one closes

    def on_ok(self, entries):
        for entry in entries:
            self.ent.append(entry.var.get())

        self.result = self.ent # save the return value to an instance variable.
        self.destroy()

class PopupCondense(tk.Toplevel):
    """modal window requires a master"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.minsize(700, 500)
        center_window(self)

        self.output = (str(master.output[0])).strip(",()\'")

        for i in range(10):
            self.columnconfigure(i, weight=1)

        for i in range(10):
            self.rowconfigure(i, weight=1)
        
        self.outputgroup = []
        self.outputsum = []
        
        lbl = tk.Label(self, text="Choose values from {} you want to keep".format(self.output))
        lbl.grid(row = 1, column = 5)

        btn1 = tk.Button(self, text='Choose Values to keep that wont be summed (GROUP BY)', command=self.open_grouppopup)
        btn1.grid(row = 2, column = 5, sticky = W+E+N+S)

        btn2 = tk.Button(self, text='Choose Values to keep that will be summed', command=self.open_sumpopup)
        btn2.grid(row= 3, column = 5, sticky = W+E+N+S)

        lbl = tk.Label(self, text="Enter a name for the new table")
        lbl.grid(row = 4, column = 5, sticky = W)

        self.ent1 = tk.Entry(self, width = 25)
        self.ent1.grid(row = 4, column = 5, sticky = E)

        btn3 = tk.Button(self, text="Create condensed table", command=self.on_ok)
        btn3.grid(row = 5, column = 5, sticky = W+E+N+S)


        # The following commands keep the popup on top.
        # Remove these if you want a program with 2 responding windows.
        # These commands must be at the end of __init__
        self.transient(master) # set to be on top of the main window
        self.grab_set() # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self) # pause anything on the main window until this one closes

    def open_grouppopup(self):
        self.group = []
        p = PopupSelectColumns(self)
        self.outputgroup = (p.result)
        for i in range(0, len(self.outputgroup), 2):
            self.group.append(self.outputgroup[i])
        lbl = tk.Label(self, text=self.group)
        lbl.grid(row = 2, column = 6)

    def open_sumpopup(self):
        self.sum = []
        p = PopupSelectColumns(self)
        self.outputsum = (p.result)
        for i in range(0, len(self.outputsum), 2):
            self.sum.append(self.outputsum[i])
        lbl = tk.Label(self, text=self.outputsum)
        lbl.grid(row = 3, column = 6)

    def on_ok(self):
        if ((self.outputsum == []) or (self.outputgroup == [])):
            lbl = tk.Label(self, text="Missing rows!") 
            lbl.grid(row = 6, column = 5)
        else:
            DB.condenseColumns(self.group, self.sum, self.output, self.ent1.get())
            self.destroy()


class PopupLoad(tk.Toplevel):
    """modal window requires a master"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.minsize(800, 400)
        center_window(self)

        for i in range(10):
            self.columnconfigure(i, weight=1)

        for i in range(10):
            self.rowconfigure(i, weight=1)

        
        lbl = tk.Label(self, text="Select the Path and Name for the file")
        lbl.grid(row = 1, column = 5, columnspan = 2)

        lbl = tk.Label(self, text="Enter file path (No quotations)")
        lbl.grid(row = 2, column = 5)

        lbl = tk.Label(self, text="Enter a name for the file")
        lbl.grid(row = 3, column = 5)

        self.ent1 = tk.Entry(self, width = 100)
        self.ent1.insert(0, r"e.g C:\Users\me\Documents\shopincome.csv")
        self.ent1.grid(row = 2, column = 6)

        self.ent2 = tk.Entry(self, width = 100)
        self.ent2.insert(0, r"e.g Income")
        self.ent2.grid(row = 3, column = 6)

        btn3 = tk.Button(self, text="Load File", command=self.on_ok)
        btn3.grid(row = 4, column = 5, sticky = W+E+N+S, columnspan = 2)


        # The following commands keep the popup on top.
        # Remove these if you want a program with 2 responding windows.
        # These commands must be at the end of __init__
        self.transient(master) # set to be on top of the main window
        self.grab_set() # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self) # pause anything on the main window until this one closes

    def on_ok(self):
        if os.path.exists(self.ent1.get()):
            DB.loadFile(self.ent1.get(), self.ent2.get())
            self.destroy()
        else:
            lbl = tk.Label(self, text="File doesn't exist!")
            lbl.grid(row = 5, column = 5, columnspan = 2)
            

class PopupGraph(tk.Toplevel):
    """modal window requires a master"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.minsize(500, 500)
        center_window(self)

        for i in range(10):
            self.columnconfigure(i, weight=1)

        for i in range(10):
            self.rowconfigure(i, weight=1)
        
        self.output = (str(master.output[0])).strip(",()\'")
        self.outputx = []
        self.outputy = []
        
        lbl = tk.Label(self, text="Choose the x and y axis value for the scatter\nPick one column per axis\nkeep this window and graph open and select new values to plot mutliple on the same graph")
        lbl.grid(row = 1, column = 5)

        btn1 = tk.Button(self, text='set x', command=self.open_xpopup)
        btn1.grid(row = 2, column = 5, sticky = W+E+N+S)

        btn2 = tk.Button(self, text='set y', command=self.open_ypopup)
        btn2.grid(row= 3, column = 5, sticky = W+E+N+S)

        btn3 = tk.Button(self, text="Create scatter graph", command=self.on_ok)
        btn3.grid(row = 4, column = 5, sticky = W+E+N+S)


        # The following commands keep the popup on top.
        # Remove these if you want a program with 2 responding windows.
        # These commands must be at the end of __init__
        self.transient(master) # set to be on top of the main window
        self.grab_set() # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self) # pause anything on the main window until this one closes

    def open_xpopup(self):
        p = PopupSelectColumns(self)
        self.outputx = (p.result[0])
        lbl = tk.Label(self, text=self.outputx)
        lbl.grid(row = 2, column = 6)

    def open_ypopup(self):
        p = PopupSelectColumns(self)
        self.outputy = (p.result[0])
        lbl = tk.Label(self, text=self.outputy)
        lbl.grid(row = 3, column = 6)

    def on_ok(self):
        if ((self.outputx[0] == 'None' or self.outputx == []) or (self.outputy[0] == 'None' or self.outputy == [])):
            lbl = tk.Label(self, text="Missing rows!") 
            lbl.grid(row = 4, column = 6)
        else:
            stat.plotScatter(self.output, self.outputx, self.outputy)
            self.destroy()


class PopupSelectColumns(tk.Toplevel):
    """modal window requires a master"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        center_window(self)

        self.table = master.output

        lbl = tk.Label(self, text="Select columns from {}".format(self.table))
        lbl.pack()

        self.ent = []

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        checkboxes = []

        text = ScrolledText(self, width=50, height=20)
        text.pack()

        cursor.execute('select * from {}'.format(self.table))
        names = list(map(lambda x: x[0], cursor.description))
        for name in names:
            if (name != "rowID"):
                checkbox_value = name
                checkbox_var = tk.BooleanVar()
                checkbox_var.set(False)  # Set the initial state (unchecked)
                checkbox = tk.Checkbutton(text, text=checkbox_value, variable=checkbox_var, bg='white', anchor = 'w')
                text.window_create('end', window=checkbox)
                text.insert('end', '\n')
                checkbox.var = checkbox_var
                checkbox.column = name
                checkboxes.append(checkbox)


        btn = tk.Button(self, text="OK", command=lambda: self.on_ok(checkboxes))
        btn.pack()

        # The following commands keep the popup on top.
        # Remove these if you want a program with 2 responding windows.
        # These commands must be at the end of __init__
        self.transient(master) # set to be on top of the main window
        self.grab_set() # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self) # pause anything on the main window until this one closes

    def on_ok(self, checkboxes):
        for box in checkboxes:
            if(box.var.get()):
                if (DB.getColumnType(self.table, box.column) == "REAL") or (DB.getColumnType(self.table, box.column) == "INTEGER"):
                    self.ent.append(box.column)
                    self.ent.append("float")
                else:
                    self.ent.append(box.column)
                    self.ent.append("string")
            
        self.result = self.ent # save the return value to an instance variable.
        self.destroy()




class PopupSelectAnyColumns(tk.Toplevel):
    """modal window requires a master"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        center_window(self)
        self.maxsize(500,600)

        lbl = tk.Label(self, text="Select 1 value for the axis")
        lbl.pack()

        self.ent = []

        try:
            self.next = master.next
        except AttributeError:
            self.next = ""

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        checkboxes = []

        text = ScrolledText(self, width=100, height=20)
        text.pack()

        for table in tables:
            cursor.execute('select * from {}'.format(table[0]))
            names = list(map(lambda x: x[0], cursor.description))
            for name in names:
                if ((name != "rowID") and (DB.getColumnType(table[0], name) == "INTEGER" or DB.getColumnType(table[0], name) == "REAL")):
                    checkbox_value = f"{table[0]} - {name}"
                    checkbox_var = tk.BooleanVar()
                    checkbox_var.set(False)  # Set the initial state (unchecked)

                    checkbox = tk.Checkbutton(text, text=checkbox_value, variable=checkbox_var, bg='white', anchor = 'w')
                    text.window_create('end', window=checkbox)
                    text.insert('end', '\n')
                    checkbox.var = checkbox_var
                    checkbox.table = table[0]
                    checkbox.row = name
                    checkboxes.append(checkbox)


        btn = tk.Button(self, text="OK", command=lambda: self.on_ok(checkboxes))
        btn.pack()

        # The following commands keep the popup on top.
        # Remove these if you want a program with 2 responding windows.
        # These commands must be at the end of __init__
        self.transient(master) # set to be on top of the main window
        self.grab_set() # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self) # pause anything on the main window until this one closes

    def on_ok(self, checkboxes):
        count = 0
        for box in checkboxes:
            if(box.var.get()):
                count += 1
        if (count != 1):
            self.ent.append("None")
        else:
            print(self.next)
            if (self.next == "Normal"):
                for box in checkboxes:
                    if(box.var.get()):
                        data = DB.selectColumn(box.table, box.row)
                        stat.plotNormalDistribution(data)
            else:
                for box in checkboxes:
                    if(box.var.get()):
                        self.ent.append(box.table)
                        self.ent.append(box.row)
            
        self.result = self.ent # save the return value to an instance variable.
        self.destroy()