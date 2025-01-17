import tkinter as tk
from tkinter import ttk, messagebox
from src.db_operations import fetch_all

class TabView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.combo=None
        self.entry_filter=None
        self.tree=None
        self.cols=[]
        self.filter_options=None
        self.opmenu=None
        self.from_price=None
        self.to_price=None
        self._build()

    def _build(self):
        tk.Label(self,text="Zobrazit Data (s filtry)",font=("Arial",11,"bold")).pack(pady=5)
        topf=tk.Frame(self)
        topf.pack(pady=5)
        tk.Label(topf,text="Tabulka:").pack(side=tk.LEFT,padx=5)
        self.combo=ttk.Combobox(topf,state="readonly")
        self.combo.pack(side=tk.LEFT,padx=5)
        tk.Button(topf,text="Načíst",command=self.load_table).pack(side=tk.LEFT,padx=5)

        fr=tk.Frame(self)
        fr.pack(pady=5)
        tk.Label(fr,text="Filtr universal:").pack(side=tk.LEFT,padx=5)
        self.entry_filter=tk.Entry(fr,width=15)
        self.entry_filter.pack(side=tk.LEFT,padx=5)
        tk.Button(fr,text="Filtrovat",command=self.filter_data).pack(side=tk.LEFT,padx=5)

        self.filter_options=tk.StringVar()
        self.filter_options.set("Vše")
        self.opmenu=ttk.OptionMenu(fr,self.filter_options,"Vše")
        self.opmenu.pack(side=tk.LEFT,padx=5)

        cf=tk.Frame(self)
        cf.pack(pady=5)
        tk.Label(cf,text="Cena/částka od:").pack(side=tk.LEFT,padx=5)
        self.from_price=tk.Entry(cf,width=8)
        self.from_price.pack(side=tk.LEFT,padx=5)
        tk.Label(cf,text="do:").pack(side=tk.LEFT,padx=5)
        self.to_price=tk.Entry(cf,width=8)
        self.to_price.pack(side=tk.LEFT,padx=5)
        tk.Button(cf,text="Filtr cena/částka",command=self.price_filter).pack(side=tk.LEFT,padx=5)

        self.frame_tree=tk.Frame(self)
        self.frame_tree.pack(fill=tk.BOTH,expand=True,pady=5)
        try:
            r=fetch_all("SHOW TABLES")
            arr=[x[0] for x in r if x[0] in ["Users","Products","Orders","OrderDetails","Categories"]]
            self.combo["values"]=arr
            if arr:self.combo.current(0)
        except:
            pass

    def load_table(self):
        t=self.combo.get()
        if not t:
            messagebox.showwarning("Upozornění","Vyberte tabulku.")
            return
        for w in self.frame_tree.winfo_children():
            w.destroy()
        self.tree=ttk.Treeview(self.frame_tree,show="headings")
        self.tree.pack(fill=tk.BOTH,expand=True)
        self.cols=[]
        try:
            d=fetch_all(f"DESCRIBE {t}")
            for c in d:
                self.cols.append(c[0])
            self.tree["columns"]=self.cols
            for c in self.cols:
                self.tree.heading(c,text=c)
                self.tree.column(c,width=120)
        except Exception as e:
            messagebox.showerror("Chyba",f"DESCRIBE:\n{e}")
            return
        self.adjust_filter_options()
        self.load_data()

    def adjust_filter_options(self):
        arr=["Vše"]
        if "IsActive" in self.cols:
            arr+=["Neaktivní","Pozastaveno"]
        if "CreatedAt" in self.cols:
            arr+=["Nejnovější","Nejstarší"]
        menu=self.opmenu["menu"]
        menu.delete(0,"end")
        for a in arr:
            menu.add_command(label=a,command=lambda val=a:self.filter_options.set(val))
        self.filter_options.set("Vše")

    def load_data(self,sql=None,params=None):
        if not sql:
            sql=f"SELECT * FROM {self.combo.get()}"
        if not params:
            params=()
        for ch in self.tree.get_children():
            self.tree.delete(ch)
        try:
            rr=fetch_all(sql,params)
            for r in rr:
                self.tree.insert("",tk.END,values=r)
        except Exception as ex:
            messagebox.showerror("Chyba",f"Nepodařilo se načíst:\n{ex}")

    def filter_data(self):
        t=self.combo.get()
        if not t:
            messagebox.showwarning("Upozornění","Vyberte tabulku.")
            return
        base=f"SELECT * FROM {t}"
        wh=[]
        pr=[]
        f=self.entry_filter.get().strip()
        if f:
            orpart=[]
            for c in self.cols:
                orpart.append(f"{c} LIKE %s")
                pr.append(f"%{f}%")
            wh.append("("+ " OR ".join(orpart)+")")
        opt=self.filter_options.get()
        if opt=="Neaktivní" and "IsActive" in self.cols:
            wh.append("IsActive='Neaktivní'")
        elif opt=="Pozastaveno" and "IsActive" in self.cols:
            wh.append("IsActive='Pozastaveno'")
        elif opt=="Nejnovější" and "CreatedAt" in self.cols:
            wh.append("1=1 ORDER BY CreatedAt DESC")
        elif opt=="Nejstarší" and "CreatedAt" in self.cols:
            wh.append("1=1 ORDER BY CreatedAt ASC")
        if wh:
            used=[]
            order_part=None
            for w in wh:
                if w.startswith("1=1 ORDER BY"):
                    order_part=w.replace("1=1 ","")
                else:
                    used.append(w)
            if used:
                base+=" WHERE "+ " AND ".join(used)
            if order_part:
                base+=" "+order_part
        self.load_data(base,tuple(pr))

    def price_filter(self):
        t=self.combo.get()
        if not t:
            messagebox.showwarning("Upozornění","Vyberte tabulku.")
            return
        if t not in ["Products","Orders"]:
            messagebox.showinfo("Info","Filtr ceny/částky jen pro Products (Price) a Orders (TotalAmount).")
            return
        f=self.from_price.get().strip()
        to=self.to_price.get().strip()
        try:
            fv=float(f) if f else 0
            tv=float(to) if to else 999999999
        except:
            messagebox.showerror("Chyba","Hodnoty musí být číselné.")
            return
        for x in self.tree.get_children():
            self.tree.delete(x)
        desc=fetch_all(f"DESCRIBE {t}")
        ccol=[xx[0] for xx in desc]
        self.tree["columns"]=ccol
        for c in ccol:
            self.tree.heading(c,text=c)
            self.tree.column(c,width=120)
        if t=="Products":
            sql="SELECT * FROM Products WHERE Price BETWEEN %s AND %s"
        else:
            sql="SELECT * FROM Orders WHERE TotalAmount BETWEEN %s AND %s"
        try:
            r=fetch_all(sql,(fv,tv))
            for row in r:
                self.tree.insert("",tk.END,values=row)
        except Exception as ex:
            messagebox.showerror("Chyba",f"Filtr se nepodařil:\n{ex}")
