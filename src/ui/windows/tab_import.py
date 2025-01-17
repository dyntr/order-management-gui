import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import json
import xml.etree.ElementTree as ET
from src.db_operations import fetch_all, execute_query

class TabImport(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.combo=None
        self._ui()

    def _ui(self):
        tk.Label(self,text="Import Dat (CSV / JSON / XML)",font=("Arial",11,"bold")).pack(pady=5)
        f=tk.Frame(self)
        f.pack(pady=5)
        tk.Button(f,text="Nápověda k formátu",command=self.help_info).pack(side=tk.LEFT,padx=5)
        tk.Button(f,text="CSV",command=lambda:self.load_file("csv")).pack(side=tk.LEFT,padx=5)
        tk.Button(f,text="JSON",command=lambda:self.load_file("json")).pack(side=tk.LEFT,padx=5)
        tk.Button(f,text="XML",command=lambda:self.load_file("xml")).pack(side=tk.LEFT,padx=5)
        tk.Label(self,text="Tabulka:").pack(pady=5)
        self.combo=ttk.Combobox(self,state="readonly")
        self.combo.pack(pady=5)
        try:
            rr=fetch_all("SHOW TABLES")
            v=[x[0] for x in rr if x[0] in ["Users","Products","Orders","OrderDetails","Categories"]]
            self.combo["values"]=v
            if v:self.combo.current(0)
        except:
            pass

    def help_info(self):
        tab=self.combo.get()
        if not tab:
            messagebox.showinfo("Nápověda","Nejprve vyberte tabulku.")
            return
        if tab=="Users":
            text=(
                "Formát pro 'Users':\n"
                "- Sloupce: Username, PasswordHash, Email, IsActive\n"
                "- PasswordHash = SHA256 hesla (např. d033e22a.. pro 'admin')\n"
                "- IsActive = 'Aktivní','Neaktivní','Pozastaveno'"
            )
        elif tab=="Products":
            text=(
                "Formát pro 'Products':\n"
                "- Sloupce: ProductName, Price, Stock, Category (název kategorie, ne ID)\n"
                "- Program si dohledá CategoryID podle tabulky 'Categories'.\n"
                "- Price= float, Stock= int."
            )
        elif tab=="Orders":
            text=(
                "Formát pro 'Orders':\n"
                "- Sloupce: UserID, TotalAmount (případně i další, pokud existují)\n"
                "- user ID musí existovat v 'Users'."
            )
        elif tab=="OrderDetails":
            text=(
                "Formát pro 'OrderDetails':\n"
                "- Sloupce: OrderID, ProductID, Quantity, PricePerUnit\n"
                "- OrderID musí existovat v 'Orders', ProductID v 'Products'."
            )
        elif tab=="Categories":
            text=(
                "Formát pro 'Categories':\n"
                "- Sloupce: Name, Description\n"
                "- Name je název kategorie.\n"
            )
        else:
            text="Vyberte tabulku."
        messagebox.showinfo(f"Nápověda: {tab}",text)

    def load_file(self,typ):
        t=self.combo.get()
        if not t:
            messagebox.showwarning("Upozornění","Nevybrali jste tabulku.")
            return
        path=filedialog.askopenfilename(filetypes=[(typ.upper(),f"*.{typ}")])
        if not path:return
        try:
            if typ=="csv":
                df=pd.read_csv(path)
            elif typ=="json":
                with open(path,"r",encoding="utf-8") as f:
                    df=pd.DataFrame(json.load(f))
            else:
                df=self._parse_xml(path)
            self._import_data(t,df)
        except Exception as ex:
            messagebox.showerror("Chyba",f"Chyba při načítání:\n{ex}")

    def _parse_xml(self,f):
        tr=ET.parse(f)
        ro=tr.getroot()
        data=[]
        for itm in ro:
            row={}
            for sub in itm:
                row[sub.tag]=sub.text
            data.append(row)
        return pd.DataFrame(data)

    def _import_data(self,tab,df):
        try:
            desc=fetch_all(f"DESCRIBE {tab}")
            allowed=[]
            for col in desc:
                if "auto_increment" not in (col[5] or "").lower():
                    allowed.append(col[0])
            dfcols=[c for c in df.columns if c in allowed]

            # Speciální případ Products => "Category" sloupec -> "CategoryID"
            # Pokud existuje 'Category' v DataFrame, dohledáme CategoryID
            if tab=="Products" and "Category" in df.columns:
                # Přejmenujeme Category => CategoryID
                # Ale musíme dohledat ID z tabulky Categories
                cat_data=[]
                for idx,rw in df.iterrows():
                    catname=rw["Category"]
                    cat_row=fetch_all("SELECT CategoryID FROM Categories WHERE Name=%s",(catname,))
                    if not cat_row:
                        raise Exception(f"Kategorie s názvem '{catname}' neexistuje v tabulce Categories.")
                    cid=cat_row[0][0]
                    # Zapíšeme do df i sloupec "CategoryID"
                    df.at[idx,"CategoryID"]=cid
                # Odebereme "Category" a nahradíme "CategoryID"
                if "CategoryID" not in dfcols:
                    dfcols.append("CategoryID")
                if "Category" in dfcols:
                    dfcols.remove("Category")

            df=df[dfcols]

            for _,row in df.iterrows():
                cns=", ".join(dfcols)
                ph=", ".join(["%s"]*len(dfcols))
                vals=tuple(row[cc] for cc in dfcols)
                execute_query(f"INSERT INTO {tab} ({cns}) VALUES ({ph})",vals)
            messagebox.showinfo("OK",f"Data importována do tabulky '{tab}'.")
        except Exception as ex:
            messagebox.showerror("Chyba",f"Import selhal:\n{ex}")
