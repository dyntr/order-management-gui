import tkinter as tk
from src.ui.windows.login import LoginWindow
from src.ui.windows.register import RegisterWindow
from src.ui.main_window import MainWindow
from src.models import User

class StartWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.chosen=None
        self.title("Úvod")
        lb=tk.Label(self,text="Vítejte.\nChcete se přihlásit nebo zaregistrovat?",padx=20,pady=20)
        lb.pack()
        f=tk.Frame(self)
        f.pack(pady=15)
        tk.Button(f,text="Přihlásit se",width=15,command=self.do_login).pack(side=tk.LEFT,padx=10)
        tk.Button(f,text="Registrovat",width=15,command=self.do_register).pack(side=tk.LEFT,padx=10)
        self.grab_set()

    def do_login(self):
        self.chosen="login"
        self.destroy()

    def do_register(self):
        self.chosen="reg"
        self.destroy()

def run_application():
    root=tk.Tk()
    root.withdraw()
    start=StartWindow(root)
    root.wait_window(start)
    if not start.chosen:
        root.destroy()
        return
    if start.chosen=="login":
        logw=LoginWindow(root)
        root.wait_window(logw)
        if not logw.accepted or not logw.user_id:
            root.destroy()
            return
        uid=logw.user_id
        u=User.find_by_id(uid)
        username = u.username if u else "unknown"
    else:
        regw=RegisterWindow(root)
        root.wait_window(regw)
        if not regw.accepted or not regw.new_id:
            root.destroy()
            return
        uid=regw.new_id
        u=User.find_by_id(uid)
        username = u.username if u else "unknown"
    root.deiconify()
    mw=MainWindow(root,uid,username)
    mw.pack(fill="both",expand=True)
    root.title("Hlavní Okno Aplikace")
    root.mainloop()
