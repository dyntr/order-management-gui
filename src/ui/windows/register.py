import tkinter as tk
from tkinter import messagebox
from src.models import User, hash_password

class RegisterWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.accepted=False
        self.new_id=None
        self.title("Registrace")
        tk.Label(self,text="Uživatelské jméno:").grid(row=0,column=0,padx=5,pady=5,sticky="e")
        self.e_user=tk.Entry(self,width=25)
        self.e_user.grid(row=0,column=1,padx=5,pady=5)
        tk.Label(self,text="Heslo:").grid(row=1,column=0,padx=5,pady=5,sticky="e")
        self.e_pass=tk.Entry(self,width=25,show="*")
        self.e_pass.grid(row=1,column=1,padx=5,pady=5)
        tk.Label(self,text="Email:").grid(row=2,column=0,padx=5,pady=5,sticky="e")
        self.e_email=tk.Entry(self,width=25)
        self.e_email.grid(row=2,column=1,padx=5,pady=5)
        self.var_active=tk.StringVar()
        self.var_active.set("Aktivní")
        tk.Label(self,text="Stav účtu:").grid(row=3,column=0,padx=5,pady=5,sticky="e")
        stavy=["Aktivní","Neaktivní","Pozastaveno"]
        cbox=tk.OptionMenu(self,self.var_active,*stavy)
        cbox.config(width=15)
        cbox.grid(row=3,column=1,padx=5,pady=5,sticky="w")
        tk.Button(self,text="Registrovat",command=self.reg).grid(row=4,column=0,columnspan=2,pady=10)
        self.grab_set()

    def reg(self):
        nm=self.e_user.get().strip()
        pw=self.e_pass.get().strip()
        em=self.e_email.get().strip()
        st=self.var_active.get()
        if not nm or not pw:
            messagebox.showwarning("Chyba","Vyplňte jméno a heslo.")
            return
        hp=hash_password(pw)
        u=User(username=nm,password_hash=hp,email=em,is_active=st)
        try:
            u.save()
            self.new_id=u.user_id
            self.accepted=True
            messagebox.showinfo("OK","Registrace proběhla úspěšně.")
            self.destroy()
        except Exception as ex:
            messagebox.showerror("Chyba",f"Nepodařilo se registrovat:\n{ex}")
