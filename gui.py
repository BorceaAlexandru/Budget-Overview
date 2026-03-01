import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from template_manager import TemplateManager
from excel_manager import ExcelManager


class BudgetApp:
    def __init__(self, root):
        self.root=root
        self.root.title("Manager Buget Lunar")
        self.root.geometry("800x600")

        self.tm=TemplateManager()

        tab_control=ttk.Notebook(root)
        self.tab_dashboard=ttk.Frame(tab_control)
        self.tab_templates=ttk.Frame(tab_control)

        tab_control.add(self.tab_dashboard, text="Dashboard & Tranzacții")
        tab_control.add(self.tab_templates, text="Administrare Template-uri")
        tab_control.pack(expand=1, fill="both")

        self._setup_dashboard()
        self._setup_templates_ui()

    def _setup_dashboard(self):
        frame=ttk.LabelFrame(self.tab_dashboard, text="1. Configurare Lună")
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="An:").pack(side="left", padx=5)
        self.var_year=tk.IntVar(value=datetime.now().year)
        ttk.Entry(frame, textvariable=self.var_year, width=6).pack(side="left")

        ttk.Label(frame, text="Luna:").pack(side="left", padx=5)
        self.var_month=tk.IntVar(value=datetime.now().month)
        ttk.Entry(frame, textvariable=self.var_month, width=4).pack(side="left")

        ttk.Button(frame, text="Generează/Actualizează Excel", command=self.process_month).pack(side="left", padx=20)

        #adaug manuala
        frame_add=ttk.LabelFrame(self.tab_dashboard, text="2. Adaugă Cheltuială Variabilă")
        frame_add.pack(fill="both", expand=True, padx=10, pady=5)

        grid_frame=ttk.Frame(frame_add)
        grid_frame.pack(pady=10)

        ttk.Label(grid_frame, text="Ziua (1-31):").grid(row=0, column=0, sticky="e")
        self.var_day=tk.IntVar(value=datetime.now().day)
        ttk.Entry(grid_frame, textvariable=self.var_day).grid(row=0, column=1)

        ttk.Label(grid_frame, text="Categorie:").grid(row=1, column=0, sticky="e")
        self.var_cat=tk.StringVar()
        ttk.Entry(grid_frame, textvariable=self.var_cat).grid(row=1, column=1)

        ttk.Label(grid_frame, text="Suma (RON):").grid(row=2, column=0, sticky="e")
        self.var_sum=tk.DoubleVar()
        ttk.Entry(grid_frame, textvariable=self.var_sum).grid(row=2, column=1)

        ttk.Label(grid_frame, text="Descriere:").grid(row=3, column=0, sticky="e")
        self.var_desc=tk.StringVar()
        ttk.Entry(grid_frame, textvariable=self.var_desc).grid(row=3, column=1)

        ttk.Button(frame_add, text="Adaugă Cheltuială", command=self.add_variable_expense).pack(pady=10)

    def _setup_templates_ui(self):
        self.tree = ttk.Treeview(self.tab_templates, columns=("Nume", "Cat", "Suma", "Zi", "Activ"), show="headings")
        self.tree.heading("Nume", text="Nume")
        self.tree.heading("Cat", text="Categorie")
        self.tree.heading("Suma", text="Suma")
        self.tree.heading("Zi", text="Zi")
        self.tree.heading("Activ", text="Activ")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree.bind("<<TreeviewSelect>>", self.on_template_select)

        form = ttk.Frame(self.tab_templates)
        form.pack(fill="x", padx=10, pady=5)

        entries=[("Nume", "tpl_name"), ("Categorie", "tpl_cat"), ("Suma", "tpl_sum"), ("Zi", "tpl_day"),
                   ("Descriere", "tpl_desc")]
        self.tpl_vars={}

        for idx, (lbl, var_name) in enumerate(entries):
            ttk.Label(form, text=lbl).grid(row=0, column=idx, padx=5)
            if var_name=="tpl_sum" or var_name=="tpl_day":
                v=tk.DoubleVar() if var_name=="tpl_sum" else tk.IntVar()
            else:
                v=tk.StringVar()
            self.tpl_vars[var_name]=v
            ttk.Entry(form, textvariable=v, width=15).grid(row=1, column=idx, padx=5)

        self.tpl_active=tk.BooleanVar(value=True)
        ttk.Checkbutton(form, text="Activ", variable=self.tpl_active).grid(row=1, column=5, padx=5)

        btn_frame = ttk.Frame(self.tab_templates)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Adaugă Nou", command=self.add_template).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Salvează Modificare", command=self.save_edit_template).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Șterge Selectat", command=self.delete_template).pack(side="left", padx=5)

        self.refresh_template_list()

    #dashboard
    def process_month(self):
        try:
            year = self.var_year.get()
            month = self.var_month.get()
            em = ExcelManager(year, month)

            em._ensure_file_exists()

            active_tpls = self.tm.get_active_templates()
            count = em.process_fixed_expenses(active_tpls)

            em.recalculate_summaries()

            msg = f"Fișier {year}-{month:02d} actualizat."
            if count > 0:
                msg += f"\nS-au adăugat {count} cheltuieli fixe noi."
            messagebox.showinfo("Succes", msg)

        except Exception as e:
            messagebox.showerror("Eroare", str(e))

    def add_variable_expense(self):
        try:
            em = ExcelManager(self.var_year.get(), self.var_month.get())
            s = self.var_sum.get()
            if s <= 0: raise ValueError("Suma trebuie să fie pozitivă.")

            em.add_transaction(
                day=self.var_day.get(),
                categorie=self.var_cat.get(),
                suma=s,
                descriere=self.var_desc.get(),
                tip="VARIABILA",
                sursa="MANUAL"
            )
            messagebox.showinfo("Succes", "Tranzacție adăugată și Excel recalculat.")
            self.var_sum.set(0)
            self.var_desc.set("")
        except Exception as e:
            messagebox.showerror("Eroare", str(e))

    def refresh_template_list(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for t in self.tm.templates:
            self.tree.insert("", "end", values=(t['nume'], t['categorie'], t['suma'], t['zi'], t['activ']))

    def add_template(self):
        self.tm.add_template(
            self.tpl_vars['tpl_name'].get(),
            self.tpl_vars['tpl_cat'].get(),
            self.tpl_vars['tpl_sum'].get(),
            self.tpl_vars['tpl_day'].get(),
            self.tpl_vars['tpl_desc'].get(),
            self.tpl_active.get()
        )
        self.refresh_template_list()

    def on_template_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])
        vals = item['values']

        idx = self.tree.index(sel[0])
        t = self.tm.templates[idx]

        self.tpl_vars['tpl_name'].set(t['nume'])
        self.tpl_vars['tpl_cat'].set(t['categorie'])
        self.tpl_vars['tpl_sum'].set(t['suma'])
        self.tpl_vars['tpl_day'].set(t['zi'])
        self.tpl_vars['tpl_desc'].set(t['descriere'])
        self.tpl_active.set(t['activ'])

    def save_edit_template(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])

        data = {
            "nume": self.tpl_vars['tpl_name'].get(),
            "categorie": self.tpl_vars['tpl_cat'].get(),
            "suma": self.tpl_vars['tpl_sum'].get(),
            "zi": self.tpl_vars['tpl_day'].get(),
            "descriere": self.tpl_vars['tpl_desc'].get(),
            "activ": self.tpl_active.get()
        }
        self.tm.update_template(idx, data)
        self.refresh_template_list()

    def delete_template(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        self.tm.delete_template(idx)
        self.refresh_template_list()