import tkinter as tk
from tkinter import ttk, messagebox
from src.db_operations import fetch_all, execute_query

class TabInsert(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.combo=None
        self.form_frame=None
        self.entries={}
        self.columns=[]
        self.dict_cat={}
        self._ui()

    def _ui(self):
        tk.Label(self,text="Vložit jeden záznam (ručně)",font=("Arial",11,"bold")).pack(pady=5)
        f=tk.Frame(self)
        f.pack(pady=5)
        tk.Label(f,text="Tabulka:").pack(side=tk.LEFT,padx=5)
        self.combo=ttk.Combobox(f,state="readonly")
        self.combo.pack(side=tk.LEFT,padx=5)
        tk.Button(f,text="Načíst sloupce",command=self.load_columns).pack(side=tk.LEFT,padx=5)
        self.form_frame=tk.Frame(self)
        self.form_frame.pack(pady=10)
        tk.Button(self,text="Odeslat do DB",command=self.submit).pack(pady=5)
        try:
            r=fetch_all("SHOW TABLES")
            v=[x[0] for x in r if x[0] in ["Users","Products","Orders","OrderDetails","Categories"]]
            self.combo["values"]=v
            if v:self.combo.current(0)
        except:
            pass

    def load_columns(self):
        t=self.combo.get()
        if not t:
            messagebox.showwarning("Upozornění","Nevybrali jste tabulku.")
            return
        for w in self.form_frame.winfo_children():
            w.destroy()
        self.entries={}
        self.columns=[]
        self.dict_cat={}
        try:
            d=fetch_all(f"DESCRIBE {t}")
            for col in d:
                if "auto_increment" not in (col[5] or "").lower():
                    self.columns.append(col[0])
        except Exception as e:
            messagebox.showerror("Chyba",f"DESCRIBE:\n{e}")
            return
        rr=0
        for c in self.columns:
            tk.Label(self.form_frame,text=c+":").grid(row=rr,column=0,padx=5,pady=5,sticky="e")
            if t=="Products" and c=="CategoryID":
                cat_box=ttk.Combobox(self.form_frame,state="readonly")
                crows=fetch_all("SELECT CategoryID,Name FROM Categories")
                arr=[]
                for cr in crows:
                    cid=cr[0]
                    cname=cr[1]
                    arr.append(cname)
                    self.dict_cat[cname]=cid
                cat_box["values"]=arr
                if arr: cat_box.current(0)
                cat_box.grid(row=rr,column=1,padx=5,pady=5)
                self.entries["CategoryID"]=cat_box
            elif t=="Users" and c=="IsActive":
                s=tk.StringVar()
                s.set("Aktivní")
                stavy=["Aktivní","Neaktivní","Pozastaveno"]
                om=ttk.OptionMenu(self.form_frame,s,"Aktivní",*stavy)
                om.grid(row=rr,column=1,padx=5,pady=5,sticky="w")
                self.entries["IsActive"]=s
            else:
                e=tk.Entry(self.form_frame,width=30)
                e.grid(row=rr,column=1,padx=5,pady=5)
                self.entries[c]=e
            rr+=1

    def submit(self):
        t=self.combo.get()
        if not t:return
        vals=[]
        colnames=[]
        for c in self.columns:
            if t=="Products" and c=="CategoryID":
                sel=self.entries["CategoryID"].get()
                if not sel:
                    messagebox.showwarning("Chyba","Musíte vybrat kategorii.")
                    return
                cid=self.dict_cat.get(sel)
                colnames.append("CategoryID")
                vals.append(cid)
            elif t=="Users" and c=="IsActive":
                st=self.entries["IsActive"].get()
                colnames.append("IsActive")
                vals.append(st)
            else:
                valobj=self.entries[c]
                if isinstance(valobj,tk.Entry):
                    v=valobj.get().strip()
                    vals.append(v)
                elif isinstance(valobj,tk.StringVar):
                    v=valobj.get()
                    vals.append(v)
                else:
                    vals.append("")
                colnames.append(c)
        cns=", ".join(colnames)
        ph=", ".join(["%s"]*len(vals))
        sql=f"INSERT INTO {t} ({cns}) VALUES ({ph})"
        try:
            execute_query(sql,tuple(vals))
            messagebox.showinfo("OK","Záznam vložen.")
        except Exception as ex:
            messagebox.showerror("Chyba",f"Chyba při vložení:\n{ex}")
