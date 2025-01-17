import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.db_operations import fetch_all

class TabReport(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.tree=None
        self.label_info=None
        self._build()

    def _build(self):
        tk.Label(self,text="Report objednávek",font=("Arial",11,"bold")).pack(pady=5)
        topf=tk.Frame(self)
        topf.pack(pady=5)
        tk.Button(topf,text="Načíst report",command=self.load_report).pack(side=tk.LEFT,padx=5)
        tk.Button(topf,text="Export CSV",command=self.export_csv).pack(side=tk.LEFT,padx=5)
        frame_tree=tk.Frame(self)
        frame_tree.pack(fill=tk.BOTH,expand=True)
        cols=("OrderID","OrderDate","Username","TotalValue")
        self.tree=ttk.Treeview(frame_tree,columns=cols,show="headings")
        for c in cols:
            self.tree.heading(c,text=c)
            self.tree.column(c,width=120)
        self.tree.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)
        sb=tk.Scrollbar(frame_tree,command=self.tree.yview)
        sb.pack(side=tk.RIGHT,fill=tk.Y)
        self.tree.configure(yscroll=sb.set)
        self.label_info=tk.Label(self,text="")
        self.label_info.pack(pady=5)

    def load_report(self):
        for x in self.tree.get_children():
            self.tree.delete(x)
        try:
            rows=fetch_all("SELECT OrderID,OrderDate,Username,TotalValue FROM OrderSummary")
            for r in rows:
                self.tree.insert("",tk.END,values=r)
            c1=fetch_all("SELECT COUNT(*) FROM Orders")[0][0]
            c2=fetch_all("SELECT IFNULL(SUM(TotalValue),0) FROM OrderSummary")[0][0]
            c3=fetch_all("SELECT IFNULL(SUM(Quantity),0) FROM OrderDetails")[0][0]
            self.label_info.config(
                text=f"Počet objednávek: {c1}\n"
                     f"Celkový obrat: {c2}\n"
                     f"Celkem kusů: {c3}"
            )
        except Exception as ex:
            messagebox.showerror("Chyba",f"Nepodařilo se načíst report:\n{ex}")

    def export_csv(self):
        data=[]
        for item in self.tree.get_children():
            data.append(self.tree.item(item,"values"))
        if not data:
            try:
                rows=fetch_all("SELECT OrderID,OrderDate,Username,TotalValue FROM OrderSummary")
                data=rows
            except:
                pass
        if not data:
            messagebox.showwarning("Upozornění","Report je prázdný, není co exportovat.")
            return
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
        if not path:
            return
        try:
            with open(path,"w",encoding="utf-8") as f:
                f.write("OrderID;OrderDate;Username;TotalValue\n")
                for r in data:
                    line=";".join(str(x) for x in r)
                    f.write(line+"\n")
            messagebox.showinfo("OK",f"Export do CSV hotov: {path}")
        except Exception as ex:
            messagebox.showerror("Chyba",f"Export selhal:\n{ex}")
