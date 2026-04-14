import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

# ── DATABASE SETUP ──────────────────────────────────────────────
DB_NAME = "students.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            reg_no   TEXT    NOT NULL UNIQUE,
            course   TEXT    NOT NULL,
            year     TEXT    NOT NULL,
            grade    TEXT,
            phone    TEXT,
            email    TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_all_students(search=""):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if search:
        c.execute("""
            SELECT id, name, reg_no, course, year, grade, phone, email
            FROM students
            WHERE name LIKE ? OR reg_no LIKE ? OR course LIKE ?
        """, (f"%{search}%", f"%{search}%", f"%{search}%"))
    else:
        c.execute("SELECT id, name, reg_no, course, year, grade, phone, email FROM students")
    rows = c.fetchall()
    conn.close()
    return rows

def add_student(name, reg_no, course, year, grade, phone, email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO students (name, reg_no, course, year, grade, phone, email)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, reg_no, course, year, grade, phone, email))
        conn.commit()
        return True, "Student added successfully!"
    except sqlite3.IntegrityError:
        return False, "Registration number already exists."
    finally:
        conn.close()

def update_student(student_id, name, reg_no, course, year, grade, phone, email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("""
            UPDATE students
            SET name=?, reg_no=?, course=?, year=?, grade=?, phone=?, email=?
            WHERE id=?
        """, (name, reg_no, course, year, grade, phone, email, student_id))
        conn.commit()
        return True, "Student updated successfully!"
    except sqlite3.IntegrityError:
        return False, "Registration number already exists."
    finally:
        conn.close()

def delete_student(student_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()

# ── MAIN APPLICATION ─────────────────────────────────────────────
class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Records Management System")
        self.root.geometry("1050x650")
        self.root.configure(bg="#F0F4F8")
        self.root.resizable(True, True)

        self.selected_id = None
        init_db()
        self.build_ui()
        self.load_students()

    def build_ui(self):
        # ── Header
        header = tk.Frame(self.root, bg="#2D5A3D", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="Student Records Management System",
                 font=("Segoe UI", 16, "bold"), bg="#2D5A3D", fg="white").pack(side="left", padx=20, pady=15)
        tk.Label(header, text="Nairobi National Polytechnic",
                 font=("Segoe UI", 10), bg="#2D5A3D", fg="#a8e6c0").pack(side="right", padx=20)

        # ── Main layout
        main = tk.Frame(self.root, bg="#F0F4F8")
        main.pack(fill="both", expand=True, padx=16, pady=12)

        left = tk.Frame(main, bg="#F0F4F8", width=320)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        right = tk.Frame(main, bg="#F0F4F8")
        right.pack(side="left", fill="both", expand=True)

        # ── Form
        form_card = tk.Frame(left, bg="white", relief="flat", bd=0)
        form_card.pack(fill="x", pady=(0, 10))
        form_card.configure(highlightbackground="#E2E8F0", highlightthickness=1)

        tk.Label(form_card, text="Student Details", font=("Segoe UI", 11, "bold"),
                 bg="white", fg="#2D5A3D").pack(anchor="w", padx=16, pady=(12, 8))

        self.fields = {}
        field_defs = [
            ("Full Name *", "name"),
            ("Registration No *", "reg_no"),
            ("Course *", "course"),
            ("Year of Study *", "year"),
            ("Grade / GPA", "grade"),
            ("Phone Number", "phone"),
            ("Email Address", "email"),
        ]

        for label_text, key in field_defs:
            tk.Label(form_card, text=label_text, font=("Segoe UI", 9),
                     bg="white", fg="#4A5568").pack(anchor="w", padx=16, pady=(4, 0))
            if key == "year":
                var = tk.StringVar(value="Year 1")
                cb = ttk.Combobox(form_card, textvariable=var,
                                  values=["Year 1", "Year 2", "Year 3", "Year 4"],
                                  font=("Segoe UI", 10), state="readonly", width=28)
                cb.pack(padx=16, pady=(0, 4), fill="x")
                self.fields[key] = var
            else:
                entry = tk.Entry(form_card, font=("Segoe UI", 10),
                                 bg="#F7FAFC", relief="flat", bd=0,
                                 highlightbackground="#CBD5E0", highlightthickness=1)
                entry.pack(padx=16, pady=(0, 4), fill="x", ipady=6)
                self.fields[key] = entry

        # Buttons
        btn_frame = tk.Frame(form_card, bg="white")
        btn_frame.pack(fill="x", padx=16, pady=(8, 14))

        self.btn_add = tk.Button(btn_frame, text="Add Student", font=("Segoe UI", 10, "bold"),
                                  bg="#2D5A3D", fg="white", relief="flat", cursor="hand2",
                                  activebackground="#1e3f2b", command=self.handle_add)
        self.btn_add.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 4))

        self.btn_update = tk.Button(btn_frame, text="Update", font=("Segoe UI", 10),
                                     bg="#C8693A", fg="white", relief="flat", cursor="hand2",
                                     activebackground="#99471d", command=self.handle_update,
                                     state="disabled")
        self.btn_update.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 4))

        self.btn_clear = tk.Button(btn_frame, text="Clear", font=("Segoe UI", 10),
                                    bg="#718096", fg="white", relief="flat", cursor="hand2",
                                    command=self.clear_form)
        self.btn_clear.pack(side="left", fill="x", expand=True, ipady=7)

        # ── Stats
        stats_card = tk.Frame(left, bg="white")
        stats_card.pack(fill="x")
        stats_card.configure(highlightbackground="#E2E8F0", highlightthickness=1)
        tk.Label(stats_card, text="Summary", font=("Segoe UI", 11, "bold"),
                 bg="white", fg="#2D5A3D").pack(anchor="w", padx=16, pady=(12, 6))
        self.lbl_total = tk.Label(stats_card, text="Total Students: 0",
                                   font=("Segoe UI", 10), bg="white", fg="#4A5568")
        self.lbl_total.pack(anchor="w", padx=16, pady=(0, 8))

        # ── Table area
        # Search bar
        search_frame = tk.Frame(right, bg="#F0F4F8")
        search_frame.pack(fill="x", pady=(0, 8))

        tk.Label(search_frame, text="Search:", font=("Segoe UI", 10),
                 bg="#F0F4F8", fg="#4A5568").pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.load_students())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                font=("Segoe UI", 10), bg="white", relief="flat",
                                highlightbackground="#CBD5E0", highlightthickness=1)
        search_entry.pack(side="left", fill="x", expand=True, ipady=6)

        # Table
        table_frame = tk.Frame(right, bg="white")
        table_frame.pack(fill="both", expand=True)
        table_frame.configure(highlightbackground="#E2E8F0", highlightthickness=1)

        cols = ("ID", "Name", "Reg No", "Course", "Year", "Grade", "Phone", "Email")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        widths = [40, 160, 100, 150, 60, 60, 110, 160]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="w")

        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28, background="white",
                         fieldbackground="white", foreground="#2D3748")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                         background="#EDF2F7", foreground="#2D5A3D")
        style.map("Treeview", background=[("selected", "#C6F6D5")], foreground=[("selected", "#1A202C")])

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Delete button
        tk.Button(right, text="Delete Selected Student", font=("Segoe UI", 10),
                  bg="#E53E3E", fg="white", relief="flat", cursor="hand2",
                  activebackground="#C53030", command=self.handle_delete).pack(pady=(8, 0), ipady=6)

    # ── ACTIONS ─────────────────────────────────────────────────
    def get_form_data(self):
        name    = self.fields["name"].get().strip()
        reg_no  = self.fields["reg_no"].get().strip()
        course  = self.fields["course"].get().strip()
        year    = self.fields["year"].get().strip()
        grade   = self.fields["grade"].get().strip()
        phone   = self.fields["phone"].get().strip()
        email   = self.fields["email"].get().strip()
        return name, reg_no, course, year, grade, phone, email

    def handle_add(self):
        name, reg_no, course, year, grade, phone, email = self.get_form_data()
        if not name or not reg_no or not course:
            messagebox.showwarning("Missing Fields", "Name, Registration No, and Course are required.")
            return
        ok, msg = add_student(name, reg_no, course, year, grade, phone, email)
        if ok:
            messagebox.showinfo("Success", msg)
            self.clear_form()
            self.load_students()
        else:
            messagebox.showerror("Error", msg)

    def handle_update(self):
        if not self.selected_id:
            return
        name, reg_no, course, year, grade, phone, email = self.get_form_data()
        if not name or not reg_no or not course:
            messagebox.showwarning("Missing Fields", "Name, Registration No, and Course are required.")
            return
        ok, msg = update_student(self.selected_id, name, reg_no, course, year, grade, phone, email)
        if ok:
            messagebox.showinfo("Success", msg)
            self.clear_form()
            self.load_students()
        else:
            messagebox.showerror("Error", msg)

    def handle_delete(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select a student to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?")
        if confirm:
            delete_student(self.selected_id)
            self.clear_form()
            self.load_students()

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])["values"]
        self.selected_id = values[0]
        keys = ["name", "reg_no", "course", "year", "grade", "phone", "email"]
        for i, key in enumerate(keys):
            val = values[i + 1]
            field = self.fields[key]
            if isinstance(field, tk.StringVar):
                field.set(val)
            else:
                field.delete(0, tk.END)
                field.insert(0, val if val else "")
        self.btn_update.config(state="normal")
        self.btn_add.config(state="disabled")

    def clear_form(self):
        for key, field in self.fields.items():
            if isinstance(field, tk.StringVar):
                field.set("Year 1")
            else:
                field.delete(0, tk.END)
        self.selected_id = None
        self.btn_update.config(state="disabled")
        self.btn_add.config(state="normal")
        self.tree.selection_remove(self.tree.selection())

    def load_students(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        search = self.search_var.get() if hasattr(self, "search_var") else ""
        rows = get_all_students(search)
        for row in rows:
            self.tree.insert("", "end", values=row)
        self.lbl_total.config(text=f"Total Students: {len(rows)}")


# ── RUN ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()
