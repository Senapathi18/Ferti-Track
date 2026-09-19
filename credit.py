# modules/credit.py — Farmer credit & seasonal billing management

import customtkinter as ctk
from tkinter import messagebox
from database import (get_all_credit_customers, get_customer_outstanding,
                      record_credit_payment, get_all_customers)
from config import PAYMENT_MODES


class CreditScreen(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color="white")
        self.pack(fill="both", expand=True)
        self.user = user

        header = ctk.CTkFrame(self, fg_color="white")
        header.pack(fill="x", padx=20, pady=(20, 4))
        ctk.CTkLabel(header, text="💳 Credit Management",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        ctk.CTkLabel(header,
                     text="Track what each farmer owes you after seasonal purchases",
                     text_color="gray", font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
        ctk.CTkButton(header, text="🔄 Refresh",
                      command=self.refresh_table).pack(side="right")

        self.table_frame = ctk.CTkScrollableFrame(self, fg_color="white")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.refresh_table()

    def refresh_table(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        headers = ["Farmer Name", "Phone", "Village", "Outstanding (₹)", "Action"]
        header_row = ctk.CTkFrame(self.table_frame, fg_color="#fff3cd")
        header_row.pack(fill="x", pady=(0, 4))
        for i, h in enumerate(headers):
            ctk.CTkLabel(header_row, text=h, font=ctk.CTkFont(weight="bold"),
                        width=150, anchor="w").grid(row=0, column=i, padx=8, pady=8)

        credit_customers = get_all_credit_customers()

        if not credit_customers:
            ctk.CTkLabel(self.table_frame,
                        text="✅ No outstanding credit balances. All farmers are paid up!",
                        text_color="green").pack(pady=40)
            return

        total_outstanding = sum(c["outstanding"] for c in credit_customers)
        ctk.CTkLabel(self.table_frame,
                    text=f"Total outstanding across all farmers: ₹{total_outstanding:,.2f}",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color="#d97706").pack(anchor="w", pady=(0, 8))

        for c in credit_customers:
            row = ctk.CTkFrame(self.table_frame, fg_color="white",
                              border_width=1, border_color="#eee")
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=c["name"], width=150, anchor="w").grid(
                row=0, column=0, padx=8, pady=8)
            ctk.CTkLabel(row, text=c["phone"] or "-", width=150, anchor="w").grid(
                row=0, column=1, padx=8, pady=8)
            ctk.CTkLabel(row, text=c["village"] or "-", width=150, anchor="w").grid(
                row=0, column=2, padx=8, pady=8)
            ctk.CTkLabel(row, text=f"₹{c['outstanding']:,.2f}", width=150,
                        anchor="w", text_color="red",
                        font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=8, pady=8)
            ctk.CTkButton(row, text="💰 Record Payment", width=140,
                         fg_color="#16a34a", hover_color="#15803d",
                         command=lambda cid=c["customer_id"], name=c["name"],
                         amt=c["outstanding"]: self.open_payment_dialog(cid, name, amt)
                        ).grid(row=0, column=4, padx=8, pady=4)

    def open_payment_dialog(self, customer_id, name, outstanding):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Record Payment — {name}")
        dialog.geometry("380x340")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Record Payment for {name}",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(20, 4))
        ctk.CTkLabel(dialog, text=f"Outstanding balance: ₹{outstanding:,.2f}",
                     text_color="red").pack(pady=4)

        amount_entry = ctk.CTkEntry(dialog, placeholder_text="Amount being paid now (₹)", width=300)
        amount_entry.pack(pady=8)
        amount_entry.insert(0, str(outstanding))   # pre-fill with full amount

        payment_dropdown = ctk.CTkComboBox(dialog, values=PAYMENT_MODES, width=300)
        payment_dropdown.pack(pady=6)
        payment_dropdown.set("Cash")

        notes_entry = ctk.CTkEntry(dialog, placeholder_text="Notes (harvest season, etc.)", width=300)
        notes_entry.pack(pady=6)

        error_label = ctk.CTkLabel(dialog, text="", text_color="red")
        error_label.pack(pady=4)

        def save_payment():
            amount = amount_entry.get().strip()
            try:
                amount = float(amount)
            except ValueError:
                error_label.configure(text="Amount must be a number.")
                return
            if amount <= 0:
                error_label.configure(text="Amount must be greater than 0.")
                return
            if amount > outstanding:
                error_label.configure(text=f"Amount cannot exceed outstanding ₹{outstanding:.2f}")
                return

            record_credit_payment(customer_id, amount,
                                 payment_mode=payment_dropdown.get(),
                                 notes=notes_entry.get().strip(),
                                 user_id=self.user["user_id"])
            messagebox.showinfo("Payment Recorded",
                               f"₹{amount:,.2f} payment recorded for {name}.\n"
                               f"Remaining: ₹{outstanding - amount:,.2f}")
            dialog.destroy()
            self.refresh_table()

        ctk.CTkButton(dialog, text="✅ Confirm Payment", width=300,
                     fg_color="#16a34a", hover_color="#15803d",
                     command=save_payment).pack(pady=16)