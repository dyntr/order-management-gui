import tkinter as tk
from tkinter import messagebox
from src.models import User, hash_password

class LoginWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.accepted=False
        self.user_id=None
        self.title("Přihlášení")
        tk.Label(self,text="Uživatelské jméno:").grid(row=0,column=0,padx=5,pady=5,sticky="e")
        self.e_user=tk.Entry(self,width=25)
        self.e_user.grid(row=0,column=1,padx=5,pady=5)
        tk.Label(self,text="Heslo:").grid(row=1,column=0,padx=5,pady=5,sticky="e")
        self.e_pass=tk.Entry(self,width=25,show="*")
        self.e_pass.grid(row=1,column=1,padx=5,pady=5)
        tk.Button(self,text="Přihlásit",command=self.ok).grid(row=2,column=0,columnspan=2,pady=10)
        self.grab_set()

    def ok(self):
        u=self.e_user.get().strip()
        p=self.e_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Chyba","Musíte vyplnit jméno i heslo.")
            return
        found=User.find_by_username_and_password(u,p)
        if not found:
            messagebox.showerror("Chyba","Neplatné údaje nebo účet není aktivní.")
            return
        self.user_id=found.user_id
        self.accepted=True
        self.destroy()
