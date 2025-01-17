import tkinter as tk
from tkinter import ttk, messagebox
from src.db_operations import fetch_all,execute_query

class TabManage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.combo=None
        self.entry_filter=None
        self.tree=None
        self.cols=[]
        self.table=None
        self.filter_options=None
        self.opmenu=None
        self._ui()

    def _ui(self):
        tk.Label(self,text="Správa Tabulky (CRUD + filtry)",font=("Arial",11,"bold")).pack(pady=5)
        topf=tk.Frame(self)
        topf.pack(pady=5)
        tk.Label(topf,text="Tabulka:").pack(side=tk.LEFT,padx=5)
        self.combo=ttk.Combobox(topf,state="readonly")
        self.combo.pack(side=tk.LEFT,padx=5)
        tk.Button(topf,text="Načíst",command=self.load_table).pack(side=tk.LEFT,padx=5)

        filtframe=tk.Frame(self)
        filtframe.pack(pady=5)
        tk.Label(filtframe,text="Filtr universal:").pack(side=tk.LEFT,padx=5)
        self.entry_filter=tk.Entry(filtframe,width=15)
        self.entry_filter.pack(side=tk.LEFT,padx=5)
        tk.Button(filtframe,text="Filtrovat",command=self.filter_data).pack(side=tk.LEFT,padx=5)

        self.filter_options=tk.StringVar()
        self.filter_options.set("Vše")
        self.opmenu=ttk.OptionMenu(filtframe,self.filter_options,"Vše")
        self.opmenu.pack(side=tk.LEFT,padx=5)

        bf=tk.Frame(self)
        bf.pack(pady=5)
        tk.Button(bf,text="Přidat",command=self.add_record).pack(side=tk.LEFT,padx=5)
        tk.Button(bf,text="Upravit",command=self.edit_record).pack(side=tk.LEFT,padx=5)
        tk.Button(bf,text="Smazat",command=self.delete_record).pack(side=tk.LEFT,padx=5)

        tf=tk.Frame(self)
        tf.pack(fill=tk.BOTH,expand=True)
        self.tree=ttk.Treeview(tf,show="headings")
        self.tree.pack(fill=tk.BOTH,expand=True)
        try:
            r=fetch_all("SHOW TABLES")
            v=[x[0] for x in r if x[0] in ["Users","Products","Orders","OrderDetails","Categories"]]
            self.combo["values"]=v
            if v:self.combo.current(0)
        except:
            pass

    def load_table(self):
        self.table=self.combo.get()
        if not self.table:
            messagebox.showwarning("Upozornění","Vyberte tabulku.")
            return
        for x in self.tree.get_children():
            self.tree.delete(x)
        self.tree["columns"]=[]
        self.cols=[]
        try:
            d=fetch_all(f"DESCRIBE {self.table}")
            for c in d:
                self.cols.append(c[0])
            self.tree["columns"]=self.cols
            for c in self.cols:
                self.tree.heading(c,text=c)
                self.tree.column(c,width=120)
        except Exception as e:
            messagebox.showerror("Chyba",f"DESCRIBE:\n{e}")
            return
        self.adjust_filter_menu()
        self.load_data()

    def adjust_filter_menu(self):
        items=["Vše"]
        if "IsActive" in self.cols:
            items+=["Neaktivní","Pozastaveno"]
        if "CreatedAt" in self.cols:
            items+=["Nejnovější","Nejstarší"]
        menu=self.opmenu["menu"]
        menu.delete(0,"end")
        for it in items:
            menu.add_command(label=it,command=lambda val=it:self.filter_options.set(val))
        self.filter_options.set("Vše")

    def load_data(self,sql=None,params=None):
        for ch in self.tree.get_children():
            self.tree.delete(ch)
        if not sql:
            sql=f"SELECT * FROM {self.table}"
        if not params:
            params=()
        try:
            rows=fetch_all(sql,params)
            for r in rows:
                self.tree.insert("",tk.END,values=r)
        except Exception as ex:
            messagebox.showerror("Chyba",f"Nepodařilo se načíst data:\n{ex}")

    def filter_data(self):
        fil=self.entry_filter.get().strip()
        opt=self.filter_options.get()
        base=f"SELECT * FROM {self.table}"
        wh=[]
        pr=[]
        if fil:
            orpart=[]
            for c in self.cols:
                orpart.append(f"{c} LIKE %s")
                pr.append(f"%{fil}%")
            wh.append("("+ " OR ".join(orpart) +")")
        sort=None
        if opt=="Neaktivní" and "IsActive" in self.cols:
            wh.append("IsActive='Neaktivní'")
        elif opt=="Pozastaveno" and "IsActive" in self.cols:
            wh.append("IsActive='Pozastaveno'")
        elif opt=="Nejnovější" and "CreatedAt" in self.cols:
            sort="ORDER BY CreatedAt DESC"
        elif opt=="Nejstarší" and "CreatedAt" in self.cols:
            sort="ORDER BY CreatedAt ASC"
        if wh:
            base+=" WHERE "+ " AND ".join(wh)
        if sort:
            base+=" "+sort
        self.load_data(base,tuple(pr))

    def add_record(self):
        if not self.table:return
        if not self.cols:return
        RecordEdit(self,self.table,self.cols,False,None)

    def edit_record(self):
        s=self.tree.focus()
        if not s:return
        val=self.tree.item(s,"values")
        RecordEdit(self,self.table,self.cols,True,val)

    def delete_record(self):
        s=self.tree.focus()
        if not s:return
        val=self.tree.item(s,"values")
        pk=val[0]
        q=messagebox.askyesno("Potvrzení",f"Opravdu chcete smazat ID={pk}?")
        if not q:return
        try:
            execute_query(f"DELETE FROM {self.table} WHERE {self.cols[0]}=%s",(pk,))
            self.load_data()
        except Exception as ex:
            messagebox.showerror("Chyba",f"Mazání selhalo:\n{ex}")

    def refresh_data(self):
        self.load_data()

class RecordEdit(tk.Toplevel):
    def __init__(self,master,table,cols,edit,rowvals):
        super().__init__(master)
        self.master=master
        self.table=table
        self.cols=cols
        self.is_edit=edit
        self.rowvals=rowvals
        self.dict_e={}
        if edit:
            self.title("Upravit záznam")
        else:
            self.title("Přidat záznam")
        r=0
        for i,c in enumerate(cols):
            if i==0:continue
            tk.Label(self,text=c+":").grid(row=r,column=0,padx=5,pady=5,sticky="e")
            e=tk.Entry(self,width=30)
            e.grid(row=r,column=1,padx=5,pady=5)
            self.dict_e[c]=e
            r+=1
        if edit and rowvals:
            idx=1
            for i,c in enumerate(cols):
                if i==0:continue
                hod=rowvals[i]
                self.dict_e[c].insert(0,str(hod) if hod is not None else "")
        tk.Button(self,text="Uložit",command=self.save).grid(row=r,column=0,columnspan=2,pady=10)

    def save(self):
        d={}
        for c in self.dict_e:
            d[c]=self.dict_e[c].get().strip()
        if not self.is_edit:
            cn=", ".join(d.keys())
            ph=", ".join(["%s"]*len(d))
            sql=f"INSERT INTO {self.table} ({cn}) VALUES ({ph})"
            pa=tuple(d.values())
        else:
            setp=", ".join([f"{k}=%s" for k in d])
            pk=self.rowvals[0]
            sql=f"UPDATE {self.table} SET {setp} WHERE {self.cols[0]}=%s"
            pa=list(d.values())
            pa.append(pk)
            pa=tuple(pa)
        try:
            execute_query(sql,pa)
            self.master.refresh_data()
            self.destroy()
        except Exception as ex:
            messagebox.showerror("Chyba",f"Operace se nezdařila:\n{ex}")
