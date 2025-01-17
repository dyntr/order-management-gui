import tkinter as tk
from tkinter import ttk, messagebox
from src.db_operations import fetch_all,execute_query

class TabSale(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.combo=None
        self.e_qty=None
        self._ui()

    def _ui(self):
        tk.Label(self,text="Prodej zboží (odečet skladu)",font=("Arial",11,"bold")).pack(pady=5)
        f=tk.Frame(self)
        f.pack(pady=5)
        tk.Label(f,text="Produkt:").grid(row=0,column=0,padx=5,pady=5,sticky="e")
        self.combo=ttk.Combobox(f,state="readonly",width=40)
        self.combo.grid(row=0,column=1,padx=5,pady=5)
        tk.Button(f,text="Obnovit",command=self.load_products).grid(row=0,column=2,padx=10,pady=5)
        tk.Label(f,text="Množství:").grid(row=1,column=0,padx=5,pady=5,sticky="e")
        self.e_qty=tk.Entry(f,width=10)
        self.e_qty.grid(row=1,column=1,padx=5,pady=5,sticky="w")
        tk.Button(self,text="Odečíst",command=self.sell).pack(pady=10)
        self.load_products()

    def load_products(self):
        try:
            rr=fetch_all("SELECT ProductID,ProductName,Stock FROM Products")
            arr=[]
            for x in rr:
                arr.append(f"{x[1]} (ID={x[0]}, Sklad={x[2]})")
            self.combo["values"]=arr
            if arr:self.combo.current(0)
        except Exception as e:
            messagebox.showerror("Chyba",f"Nepodařilo se načíst produkty:\n{e}")

    def sell(self):
        s=self.combo.get()
        if not s:
            messagebox.showwarning("Upozornění","Vyberte produkt.")
            return
        try:
            i1=s.index("ID=")+3
            i2=s.index(",",i1)
            pid=int(s[i1:i2])
        except:
            messagebox.showerror("Chyba","Nepodařilo se zjistit ID produktu.")
            return
        val=self.e_qty.get().strip()
        try:
            q=int(val)
        except:
            messagebox.showerror("Chyba","Množství musí být celé číslo.")
            return
        if q<=0:
            messagebox.showerror("Chyba","Množství musí být kladné.")
            return
        try:
            st=fetch_all("SELECT Stock FROM Products WHERE ProductID=%s",(pid,))
            if not st:
                messagebox.showerror("Chyba","Produkt neexistuje.")
                return
            skl=st[0][0]
            if skl<q:
                messagebox.showerror("Chyba",f"Nedostatek na skladě (máme {skl}).")
                return
            execute_query("UPDATE Products SET Stock=Stock - %s WHERE ProductID=%s",(q,pid))
            messagebox.showinfo("OK","Odečteno.")
            self.load_products()
        except Exception as ex:
            messagebox.showerror("Chyba",f"Chyba odečtu:\n{ex}")
