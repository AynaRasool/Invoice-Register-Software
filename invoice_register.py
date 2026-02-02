import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

selected_invoice_id = None

# ---------------- PROFESSIONAL STYLED BUTTON ----------------
def styled_button(parent, text, command, bg, fg="white"):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        padx=16,
        pady=8,
        cursor="hand2",
        activebackground=bg,
        activeforeground=fg,
        bd=0
    )

    # Hover effect
    def brighten_color(color, factor=1.12):
        color = color.lstrip('#')
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        r = min(int(r * factor), 255)
        g = min(int(g * factor), 255)
        b = min(int(b * factor), 255)
        return f"#{r:02X}{g:02X}{b:02X}"

    hover_bg = brighten_color(bg)

    def on_enter(e):
        btn['bg'] = hover_bg

    def on_leave(e):
        btn['bg'] = bg

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    return btn

# ---------------- MODERN ENTRY ----------------
def modern_entry(parent):
    default_bg = "#D1D5DB"  # slightly darker gray
    focus_bg = "#E0E7FF"    # soft blue when focused

    frame = tk.Frame(parent, bg=default_bg, bd=0, highlightthickness=0, padx=5, pady=2)
    entry = tk.Entry(frame, bd=0, font=("Segoe UI", 10), bg=default_bg, fg="#111827", insertbackground="#111827")
    entry.pack(fill=tk.X, padx=5, pady=2)

    def on_focus_in(e):
        entry.config(bg=focus_bg)

    def on_focus_out(e):
        entry.config(bg=default_bg)

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

    frame.pack(fill=tk.X, pady=5)
    return entry

# ---------------- DATABASE ----------------
conn = sqlite3.connect("invoices.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no TEXT,
    invoice_date TEXT,
    amount REAL
)
""")
conn.commit()

# ---------------- FUNCTIONS ----------------
def clear_fields():
    entry_invoice.delete(0, tk.END)
    entry_date.delete(0, tk.END)
    entry_amount.delete(0, tk.END)
    entry_date.insert(0, datetime.now().strftime("%d/%m/%Y"))

def load_invoices():
    table.delete(*table.get_children())
    cursor.execute("SELECT id, invoice_no, invoice_date, amount FROM invoices ORDER BY invoice_date")
    rows = cursor.fetchall()
    for index, row in enumerate(rows, start=1):
        tag = 'evenrow' if index % 2 == 0 else 'oddrow'
        display_date = datetime.strptime(row[2], "%Y-%m-%d").strftime("%d/%m/%Y")
        table.insert("", tk.END, values=(index, row[1], display_date, f"{row[3]:,.2f}"), tags=(row[0], tag))

def add_invoice():
    try:
        date_obj = datetime.strptime(entry_date.get(), "%d/%m/%Y")
        date_for_db = date_obj.strftime("%Y-%m-%d")  # store in ISO format
        amount = float(entry_amount.get())
    except:
        messagebox.showerror("Error", "Invalid date or amount")
        return

    cursor.execute("INSERT INTO invoices (invoice_no, invoice_date, amount) VALUES (?, ?, ?)",
                   (entry_invoice.get(), date_for_db, amount))
    conn.commit()
    load_invoices()
    clear_fields()
    show_popup("✅ Invoice added successfully", popup_type="success")  # popup notification



def select_invoice(event):
    global selected_invoice_id
    selected = table.focus()
    if not selected:
        return

    values = table.item(selected, "values")
    selected_invoice_id = table.item(selected, "tags")[0]  # DB ID stored in tags

    entry_invoice.delete(0, tk.END)
    entry_date.delete(0, tk.END)
    entry_amount.delete(0, tk.END)

    entry_invoice.insert(0, values[1])
    entry_date.insert(0, values[2])
    entry_amount.insert(0, values[3].replace(",", ""))

def update_invoice():
    global selected_invoice_id
    if not selected_invoice_id:
        messagebox.showerror("Error", "Select an invoice to update")
        return

    try:
        date_obj = datetime.strptime(entry_date.get(), "%d/%m/%Y")
        date_for_db = date_obj.strftime("%Y-%m-%d")
        amount = float(entry_amount.get())
    except:
        messagebox.showerror("Error", "Invalid date or amount")
        return

    cursor.execute("""
        UPDATE invoices
        SET invoice_no=?, invoice_date=?, amount=?
        WHERE id=?
    """, (entry_invoice.get(), date_for_db, amount, selected_invoice_id))
    conn.commit()
    load_invoices()
    clear_fields()
    show_popup("✏️ Invoice updated", popup_type="info")  # popup notification

def delete_invoice():
    selected = table.focus()
    if not selected:
        messagebox.showwarning("Select Invoice", "Please select an invoice to delete.")
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this invoice?"
    )

    if not confirm:
        return

    invoice_id = table.item(selected)["tags"][0]
    cursor.execute("DELETE FROM invoices WHERE id=?", (invoice_id,))
    conn.commit()

    load_invoices()
    clear_fields()
    show_popup("🗑️ Invoice deleted successfully", popup_type="error")



def calculate_yearly_total():
    year = entry_year.get()
    if not year.isdigit() or len(year) != 4:
        messagebox.showerror("Error", "Please enter a valid 4-digit year")
        return

    cursor.execute("SELECT SUM(amount) FROM invoices WHERE strftime('%Y', invoice_date)=?", (year,))
    total = cursor.fetchone()[0] or 0
    label_total.config(text=f"{total:,.2f}")

# ---------------- UI ----------------
root = tk.Tk()
root.title("Invoice Register System")
root.geometry("950x520")
root.configure(bg="#F3F4F6")

# ---------------- POPUP NOTIFICATION ----------------
def show_popup(message, duration=2000, popup_type="info"):
    """
    Modern centered popup with dynamic width/height based on message length.
    Single-line, professional style.
    """
    popup = tk.Toplevel(root)
    popup.overrideredirect(True)
    popup.attributes("-topmost", True)
    popup.attributes("-alpha", 0.0)  # start transparent

    # Professional colors + Unicode icons
    colors = {
        "info": ("#2A3345", "\u2139"),      # ℹ
        "success": ("#28643F", "\u2714"),   # ✔
        "warning": ("#513E2A", "\u26A0"),   # ⚠
        "error": ("#962D2D", "\u2716")      # ✖
    }
    bg_color, icon = colors.get(popup_type, ("#395799", "\u2139"))

    # Font for measuring text
    font = ("Segoe UI", 11, "bold")
    temp_label = tk.Label(root, text=f"{icon}  {message}", font=font)
    temp_label.update_idletasks()
    text_width = temp_label.winfo_reqwidth() + 40   # padding
    text_height = temp_label.winfo_reqheight() + 20

    width = min(text_width, root.winfo_width() - 40)  # max width limit
    height = text_height

    # Center position
    root.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)

    popup.geometry(f"{width}x{height}+{x}+{y}")

    # Shadow effect
    shadow_offset = 3
    shadow = tk.Frame(popup, bg="#888888")
    shadow.place(x=shadow_offset, y=shadow_offset, width=width, height=height)

    # Main frame
    frame = tk.Frame(popup, bg=bg_color)
    frame.place(x=0, y=0, width=width-shadow_offset, height=height-shadow_offset)

    # Label with icon + message
    label = tk.Label(
        frame,
        text=f"{icon}  {message}",
        bg=bg_color,
        fg="white",
        font=font,
        anchor="center",
        justify="center",
        padx=10,
        pady=5
    )
    label.pack(fill=tk.BOTH, expand=True)

    # Fade animation
    alpha = 0.0
    increment = 0.05

    def fade_in():
        nonlocal alpha
        alpha = min(alpha + increment, 1.0)
        popup.attributes("-alpha", alpha)
        if alpha < 1.0:
            popup.after(20, fade_in)
        else:
            popup.after(duration, fade_out)

    def fade_out():
        nonlocal alpha
        alpha = max(alpha - increment, 0.0)
        popup.attributes("-alpha", alpha)
        if alpha > 0.0:
            popup.after(20, fade_out)
        else:
            popup.destroy()

    fade_in()


# LEFT FRAME
left = tk.Frame(root, bg="#ffffff", padx=20, pady=20,
                highlightbackground="#A78BFA", highlightthickness=2)
left.pack(side=tk.LEFT, fill=tk.Y)

tk.Label(left, text="Invoice Form", font=("Segoe UI", 15, "bold"), bg="#ffffff", fg="#4F46E5").pack(anchor="w", pady=(0, 10))

tk.Label(left, text="Invoice No", bg="#ffffff").pack(anchor="w")
entry_invoice = modern_entry(left)

tk.Label(left, text="Date (DD/MM/YYYY)", bg="#ffffff").pack(anchor="w")
entry_date = modern_entry(left)
entry_date.insert(0, datetime.now().strftime("%d/%m/%Y"))

tk.Label(left, text="Amount", bg="#ffffff").pack(anchor="w")
entry_amount = modern_entry(left)

# Buttons
btn_frame = tk.Frame(left, bg="#ffffff")
btn_frame.pack(pady=10)
styled_button(btn_frame, "Add", add_invoice, "#38945A").grid(row=0, column=0, padx=5)
styled_button(btn_frame, "Update", update_invoice, "#3885A5").grid(row=0, column=1, padx=5)
styled_button(btn_frame, "Delete", delete_invoice, "#CE2F2F").grid(row=0, column=2, padx=5)

# Yearly Total
tk.Label(left, text="Yearly Total", font=("Segoe UI", 13, "bold"), bg="#ffffff", fg="#4F46E5").pack(anchor="w", pady=(20,5))
entry_year = modern_entry(left)

styled_button(left, "Calculate", calculate_yearly_total, "#6852AA").pack(pady=5)
label_total = tk.Label(left, text="0.00", font=("Segoe UI", 16, "bold"), fg="#2e7d32", bg="#ffffff")
label_total.pack(pady=(5,10))

# RIGHT TABLE
right = tk.Frame(root, bg="#E0E7FF", padx=20, pady=20)
right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

style = ttk.Style()
style.configure("Treeview", background="#ffffff", foreground="#111827",
                rowheight=28, fieldbackground="#E0E7FF", font=("Segoe UI", 10))
style.map("Treeview", background=[("selected", "#A78BFA")], foreground=[("selected", "#1e3a8a")])
style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

table = ttk.Treeview(right, columns=("#", "Invoice No", "Date", "Amount"), show="headings")
for col, width, anchor in [("#",50,"center"), ("Invoice No",150,"center"), ("Date",120,"center"), ("Amount",120,"center")]:
    table.heading(col, text=col)
    table.column(col, width=width, anchor=anchor)

table.tag_configure('oddrow', background="#ffffff")
table.tag_configure('evenrow', background="#E0E7FF")

table.pack(fill=tk.BOTH, expand=True)
scrollbar = ttk.Scrollbar(right, orient="vertical", command=table.yview)
table.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

table.bind("<<TreeviewSelect>>", select_invoice)

load_invoices()

# ---------------- STATUS BAR ----------------
status_var = tk.StringVar()
status_var.set("Ready")  # initial status

status_label = tk.Label(
    root,
    textvariable=status_var,
    bg="#f4f6f8",
    fg="#374151",
    font=("Segoe UI", 9),
    anchor="w",
    padx=10
)
status_label.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()
