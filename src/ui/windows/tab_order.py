import tkinter as tk
from tkinter import ttk, messagebox
from src.models import Order,OrderDetail
from src.db_operations import fetch_all

class TabOrder(tk.Frame):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.user_id=user_id
        self.items=[]
        self.tree=None
        self.label_sum=None
        self._build_ui()

    def _build_ui(self):
        tk.Label(self,text="Nová Objednávka",font=("Arial",11,"bold")).pack(pady=5)
        frm=tk.Frame(self)
        frm.pack(fill=tk.BOTH,expand=True)
        self.tree=ttk.Treeview(frm,columns=("Produkt","Množství","Cena","Celkem"),show="headings")
        for c in ("Produkt","Množství","Cena","Celkem"):
            self.tree.heading(c,text=c)
            self.tree.column(c,width=120)
        self.tree.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)
        sb=tk.Scrollbar(frm,command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side=tk.RIGHT,fill=tk.Y)
        bf=tk.Frame(self)
        bf.pack(pady=5)
        tk.Button(bf,text="Přidat položku",command=self.add_item).pack(side=tk.LEFT,padx=5)
        tk.Button(bf,text="Odebrat položku",command=self.remove_item).pack(side=tk.LEFT,padx=5)
        tk.Button(bf,text="Vytvořit objednávku",command=self.make_order).pack(side=tk.LEFT,padx=5)
        self.label_sum=tk.Label(self,text="Počet ks: 0  Celkem: 0.00")
        self.label_sum.pack(pady=5)

    def add_item(self):
        OrderItemDialog(self)

    def remove_item(self):
        sel=self.tree.focus()
        if not sel:return
        v=self.tree.item(sel,"values")
        if not v:return
        idx=None
        for i,x in enumerate(self.items):
            if x[0]==v[0] and x[2]==float(v[1]) and x[3]==float(v[2]):
                idx=i
                break
        if idx!=None:
            self.items.pop(idx)
        self.tree.delete(sel)
        self._recalc()

    def make_order(self):
        if not self.items:
            messagebox.showerror("Chyba","Objednávka je prázdná.")
            return
        total=0.0
        details=[]
        for it in self.items:
            total+=it[2]*it[3]
            details.append(OrderDetail(product_id=it[1],quantity=int(it[2]),price_per_unit=float(it[3])))
        o=Order(user_id=self.user_id,total_amount=total)
        o.details=details
        try:
            o.save()
            messagebox.showinfo("OK",f"Objednávka vytvořena! ID={o.order_id}")
            self.items.clear()
            for xx in self.tree.get_children():
                self.tree.delete(xx)
            self.label_sum.config(text="Počet ks: 0  Celkem: 0.00")
        except Exception as ex:
            messagebox.showerror("Chyba",f"{ex}")

    def add_row(self,name,pid,qty,price):
        self.items.append((name,pid,qty,price))
        tot=qty*price
        self.tree.insert("",tk.END,values=(name,str(qty),str(price),f"{tot:.2f}"))
        self._recalc()

    def _recalc(self):
        ks=0
        cc=0.0
        for x in self.items:
            ks+=x[2]
            cc+=x[2]*x[3]
        self.label_sum.config(text=f"Počet ks: {int(ks)}  Celkem: {cc:.2f}")

class OrderItemDialog(tk.Toplevel):
    def __init__(self, par):
        super().__init__(par)
        self.par=par
        self.title("Položka objednávky")
        self.data=[]
        tk.Label(self,text="Název produktu:").grid(row=0,column=0,padx=5,pady=5,sticky="e")
        self.e_name=tk.Entry(self,width=25)
        self.e_name.grid(row=0,column=1,padx=5,pady=5)
        self.e_name.bind("<KeyRelease>",self._on_filter)
        self.list=tk.Listbox(self,width=35,height=5)
        self.list.grid(row=1,column=0,columnspan=2,padx=5,pady=5)
        self.list.bind("<<ListboxSelect>>",self._on_select)
        tk.Label(self,text="Cena:").grid(row=2,column=0,padx=5,pady=5,sticky="e")
        self.e_price=tk.Entry(self,width=10)
        self.e_price.grid(row=2,column=1,padx=5,pady=5,sticky="w")
        tk.Label(self,text="Množství:").grid(row=3,column=0,padx=5,pady=5,sticky="e")
        self.e_qty=tk.Entry(self,width=10)
        self.e_qty.grid(row=3,column=1,padx=5,pady=5,sticky="w")
        tk.Button(self,text="Přidat",command=self._ok).grid(row=4,column=0,columnspan=2,pady=10)
        self.grab_set()

    def _on_filter(self,e):
        t=self.e_name.get().strip()
        self.list.delete(0,tk.END)
        self.data=[]
        if not t:return
        try:
            rr=fetch_all("SELECT ProductID,ProductName,Price FROM Products WHERE ProductName LIKE %s LIMIT 20",(f"%{t}%",))
            self.data=rr
            for x in rr:
                self.list.insert(tk.END,f"{x[1]} (ID={x[0]})")
        except:
            pass

    def _on_select(self,e):
        idx=self.list.curselection()
        if not idx:return
        i=idx[0]
        pid,pname,price=self.data[i]
        self.e_name.delete(0,tk.END)
        self.e_name.insert(0,pname)
        self.e_price.delete(0,tk.END)
        self.e_price.insert(0,str(price))

    def _ok(self):
        nm=self.e_name.get().strip()
        ps=self.e_price.get().strip()
        qs=self.e_qty.get().strip()
        if not nm or not ps or not qs:
            messagebox.showerror("Chyba","Vyplňte název, cenu i množství.")
            return
        try:
            pr=float(ps)
            qt=float(qs)
        except:
            messagebox.showerror("Chyba","Cena a množství musí být číslo.")
            return
        pid=None
        for d in self.data:
            if d[1]==nm and abs(d[2]-pr)<0.0001:
                pid=d[0]
                break
        if not pid:
            ro=fetch_all("SELECT ProductID,Price FROM Products WHERE ProductName=%s",(nm,))
            if not ro:
                messagebox.showerror("Chyba","Produkt neexistuje v DB.")
                return
            pid=ro[0][0]
        self.par.add_row(nm,pid,qt,pr)
        self.destroy()
