import tkinter as tk
from tkinter import ttk
from src.ui.windows.tab_import import TabImport
from src.ui.windows.tab_insert import TabInsert
from src.ui.windows.tab_manage import TabManage
from src.ui.windows.tab_order import TabOrder
from src.ui.windows.tab_sale import TabSale
from src.ui.windows.tab_view import TabView
from src.ui.windows.tab_report import TabReport

class MainWindow(tk.Frame):
    def __init__(self, master, user_id, username):
        super().__init__(master)
        self.master=master
        self.user_id=user_id
        self.username=username
        self.notebook=ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH,expand=True)

        self.tab_import=TabImport(self.notebook)
        self.notebook.add(self.tab_import,text="Import Dat")

        self.tab_insert=TabInsert(self.notebook)
        self.notebook.add(self.tab_insert,text="Vložit Záznam")

        self.tab_manage=TabManage(self.notebook)
        self.notebook.add(self.tab_manage,text="Správa Tabulky")

        self.tab_order=TabOrder(self.notebook,self.user_id)
        self.notebook.add(self.tab_order,text="Objednávka")

        self.tab_sale=TabSale(self.notebook)
        self.notebook.add(self.tab_sale,text="Prodej")

        self.tab_view=TabView(self.notebook)
        self.notebook.add(self.tab_view,text="Zobrazit Data")

        self.tab_report=TabReport(self.notebook)
        self.notebook.add(self.tab_report,text="Reporty")

        btn_text=f"Odhlásit uživatele {self.username}"
        self.btn_logout=tk.Button(self,text=btn_text,command=self.logout)
        self.btn_logout.pack(pady=5)

    def logout(self):
        self.master.destroy()
