import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import date, datetime

FILE_NAME = "expenses.csv"
CATEGORIES = ["Food", "Travel", "Shopping", "Education", "Other"]

PURPLE = "#7652C8"
DARK_PURPLE = "#39256B"
BG = "#F8F6FF"
LAVENDER = "#EEE8FF"
WHITE = "#FFFFFF"


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Expense Tracker")
        self.root.geometry("900x650")
        self.root.minsize(750, 550)
        self.root.configure(bg=BG)

        self.expenses = []
        self.next_id = 1

        self.create_widgets()
        self.load_expenses()
        self.update_display()

    def create_widgets(self):
        # Heading
        tk.Label(
            self.root,
            text="STUDENT EXPENSE TRACKER",
            font=("Arial", 22, "bold"),
            bg=PURPLE,
            fg=WHITE,
            pady=15
        ).pack(fill="x")

        tk.Label(
            self.root,
            text="Record and manage your daily expenses",
            font=("Arial", 11),
            bg=BG,
            fg=DARK_PURPLE
        ).pack(pady=8)

        # Summary
        summary = tk.Frame(self.root, bg=BG)
        summary.pack(fill="x", padx=20, pady=8)

        self.total_label = tk.Label(
            summary, text="Total Spending: ₹0.00",
            font=("Arial", 13, "bold"),
            bg=LAVENDER, fg=DARK_PURPLE, pady=12
        )
        self.total_label.pack(side="left", fill="x", expand=True, padx=5)

        self.count_label = tk.Label(
            summary, text="Transactions: 0",
            font=("Arial", 13, "bold"),
            bg=LAVENDER, fg=DARK_PURPLE, pady=12
        )
        self.count_label.pack(side="left", fill="x", expand=True, padx=5)

        # Input form
        form = tk.LabelFrame(
            self.root, text=" Add New Expense ",
            font=("Arial", 11, "bold"),
            bg=WHITE, fg=DARK_PURPLE, padx=12, pady=10
        )
        form.pack(fill="x", padx=20, pady=8)

        tk.Label(form, text="Expense Name", bg=WHITE).grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.name_entry = tk.Entry(form, width=22)
        self.name_entry.grid(row=1, column=0, padx=5, pady=5)

        tk.Label(form, text="Amount (₹)", bg=WHITE).grid(
            row=0, column=1, sticky="w", padx=5, pady=5
        )
        self.amount_entry = tk.Entry(form, width=15)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form, text="Category", bg=WHITE).grid(
            row=0, column=2, sticky="w", padx=5, pady=5
        )
        self.category_combo = ttk.Combobox(
            form, values=CATEGORIES, state="readonly", width=16
        )
        self.category_combo.set("Food")
        self.category_combo.grid(row=1, column=2, padx=5, pady=5)

        tk.Label(form, text="Date (YYYY-MM-DD)", bg=WHITE).grid(
            row=0, column=3, sticky="w", padx=5, pady=5
        )
        self.date_entry = tk.Entry(form, width=15)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=1, column=3, padx=5, pady=5)

        # Buttons - kept in their own row so they remain visible
        buttons = tk.Frame(self.root, bg=BG)
        buttons.pack(fill="x", padx=20, pady=8)

        tk.Button(
            buttons, text="Add Expense",
            command=self.add_expense,
            bg=PURPLE, fg=WHITE, padx=12, pady=7
        ).pack(side="left", padx=5)

        tk.Button(
            buttons, text="Delete Selected",
            command=self.delete_expense,
            bg="#FCE5EA", fg="#A92E50", padx=12, pady=7
        ).pack(side="left", padx=5)

        tk.Button(
            buttons, text="Save Expenses",
            command=self.save_expenses,
            bg="#DDF4E8", fg="#205D42", padx=12, pady=7
        ).pack(side="left", padx=5)

        tk.Button(
            buttons, text="Clear Fields",
            command=self.clear_fields,
            bg=LAVENDER, fg=DARK_PURPLE, padx=12, pady=7
        ).pack(side="left", padx=5)

        # Expense table
        table_frame = tk.LabelFrame(
            self.root, text=" Expense History ",
            font=("Arial", 11, "bold"),
            bg=WHITE, fg=DARK_PURPLE
        )
        table_frame.pack(
            fill="both", expand=True, padx=20, pady=(5, 18)
        )

        columns = ("name", "amount", "category", "date")
        self.tree = ttk.Treeview(
            table_frame, columns=columns,
            show="headings", selectmode="extended"
        )

        self.tree.heading("name", text="Expense Name")
        self.tree.heading("amount", text="Amount (₹)")
        self.tree.heading("category", text="Category")
        self.tree.heading("date", text="Date")

        self.tree.column("name", width=230)
        self.tree.column("amount", width=130, anchor="center")
        self.tree.column("category", width=150, anchor="center")
        self.tree.column("date", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Table styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=WHITE,
            fieldbackground=WHITE,
            rowheight=27,
            font=("Arial", 10)
        )
        style.configure(
            "Treeview.Heading",
            background=LAVENDER,
            foreground=DARK_PURPLE,
            font=("Arial", 10, "bold")
        )

    def add_expense(self):
        name = self.name_entry.get().strip()
        amount_text = self.amount_entry.get().strip()
        category = self.category_combo.get()
        expense_date = self.date_entry.get().strip()

        if not name:
            messagebox.showwarning(
                "Invalid Input", "Please enter an expense name."
            )
            return

        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Invalid Amount",
                "Enter a valid amount greater than zero."
            )
            return

        try:
            datetime.strptime(expense_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning(
                "Invalid Date", "Use the format YYYY-MM-DD."
            )
            return

        if category not in CATEGORIES:
            messagebox.showwarning(
                "Invalid Category", "Please choose a category."
            )
            return

        expense = {
            "id": self.next_id,
            "name": name,
            "amount": amount,
            "category": category,
            "date": expense_date
        }

        self.expenses.append(expense)
        self.next_id += 1

        self.update_display()
        self.clear_fields()

    def delete_expense(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select an expense to delete."
            )
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete the selected expense(s)?"
        ):
            return

        selected_ids = {int(item) for item in selected}

        self.expenses = [
            expense for expense in self.expenses
            if expense["id"] not in selected_ids
        ]

        self.update_display()

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.category_combo.set("Food")

        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().isoformat())

    def save_expenses(self):
        try:
            with open(
                FILE_NAME, "w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.writer(file)

                writer.writerow([
                    "Name", "Amount", "Category", "Date"
                ])

                for expense in self.expenses:
                    writer.writerow([
                        expense["name"],
                        expense["amount"],
                        expense["category"],
                        expense["date"]
                    ])

            messagebox.showinfo(
                "Saved",
                "Your expenses have been saved successfully!"
            )

        except OSError as error:
            messagebox.showerror(
                "Save Error", str(error)
            )

    def load_expenses(self):
        if not os.path.exists(FILE_NAME):
            return

        try:
            with open(
                FILE_NAME, "r", newline="", encoding="utf-8"
            ) as file:
                rows = list(csv.reader(file))

            # Skip the header if present
            if rows and rows[0][0].strip().lower() == "name":
                rows = rows[1:]

            for row in rows:
                if len(row) < 3:
                    continue

                try:
                    name = row[0].strip()
                    amount = float(row[1])
                    category = row[2].strip()

                    expense_date = (
                        row[3].strip()
                        if len(row) >= 4
                        else date.today().isoformat()
                    )

                    datetime.strptime(expense_date, "%Y-%m-%d")

                    if name and amount > 0 and category in CATEGORIES:
                        self.expenses.append({
                            "id": self.next_id,
                            "name": name,
                            "amount": amount,
                            "category": category,
                            "date": expense_date
                        })
                        self.next_id += 1

                except (ValueError, IndexError):
                    continue

        except (OSError, csv.Error) as error:
            messagebox.showerror("Load Error", str(error))

    def update_display(self):
        total = sum(
            expense["amount"] for expense in self.expenses
        )
        count = len(self.expenses)

        self.total_label.config(
            text=f"Total Spending: ₹{total:,.2f}"
        )
        self.count_label.config(
            text=f"Transactions: {count}"
        )

        for item in self.tree.get_children():
            self.tree.delete(item)

        ordered = sorted(
            self.expenses,
            key=lambda expense: (expense["date"], expense["id"]),
            reverse=True
        )

        for expense in ordered:
            self.tree.insert(
                "", "end",
                iid=str(expense["id"]),
                values=(
                    expense["name"],
                    f'{expense["amount"]:,.2f}',
                    expense["category"],
                    expense["date"]
                )
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()