# modules/inward.py

import customtkinter as ctk
from tkinter import messagebox
from database import (add_inward_stock, get_all_products,
                      get_inward_history, delete_inward_entry)


class InwardScreen(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color="white")
        self.pack(fill="both", expand=True)
        self.user = user

        header = ctk.CTkFrame(self, fg_color="white")
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(header, text="⬇️ Inward Stock",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color="#1a1a1a").pack(side="left")
        ctk.CTkButton(header, text="+ Add Stock Entry",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self.open_add_dialog).pack(side="right")

        self.table_frame = ctk.CTkScrollableFrame(self, fg_color="white")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.refresh_table()

    def refresh_table(self):
        for w in self.table_frame.winfo_children():
            w.destroy()

        headers = ["Product", "Supplier", "Qty", "Price (₹)",
                   "Expiry", "Date", "Action"]
        hr = ctk.CTkFrame(self.table_frame, fg_color="#f0f4f8")
        hr.pack(fill="x", pady=(0, 4))
        for i, h in enumerate(headers):
            ctk.CTkLabel(hr, text=h,
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="#1a1a1a", width=120, anchor="w").grid(
                row=0, column=i, padx=6, pady=8)

        entries = get_inward_history()
        if not entries:
            ctk.CTkLabel(self.table_frame,
                        text="No inward stock entries yet. Click '+ Add Stock Entry'.",
                        text_color="gray",
                        font=ctk.CTkFont(size=13)).pack(pady=40)
            return

        for e in entries:
            e = dict(e)
            row = ctk.CTkFrame(self.table_frame, fg_color="white",
                              border_width=1, border_color="#eee")
            row.pack(fill="x", pady=2)

            for i, val in enumerate([
                e["product_name"], e["supplier_name"],
                str(e["quantity_received"]),
                f"₹{e['purchase_price']:.2f}",
                e["expiry_date"] or "-",
                str(e["date_of_entry"])[:10],
            ]):
                ctk.CTkLabel(row, text=val, width=120, anchor="w",
                            font=ctk.CTkFont(size=12),
                            text_color="#1a1a1a").grid(
                    row=0, column=i, padx=6, pady=8)

            ctk.CTkButton(
                row, text="🗑️ Delete", width=90,
                fg_color="#e74c3c", hover_color="#c0392b",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda iid=e["inward_id"]: self.confirm_delete(iid)
            ).grid(row=0, column=6, padx=6, pady=4)

    def confirm_delete(self, inward_id):
        if messagebox.askyesno(
                "Delete Entry",
                "Remove this stock entry?\n\n"
                "⚠️ This will affect current stock calculations."):
            delete_inward_entry(inward_id)
            messagebox.showinfo("Deleted", "Stock entry removed.")
            self.refresh_table()

    def open_add_dialog(self):
        products = get_all_products()
        if not products:
            messagebox.showwarning(
                "No Products",
                "Add a product first before adding stock.")
            return

        product_names = [p["product_name"] for p in products]
        product_map = {p["product_name"]: dict(p) for p in products}

        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Inward Stock")
        dialog.geometry("420x500")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Add Inward Stock Entry",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))

        fields = {}
        placeholders = [
            ("product", "Select product", True, product_names),
            ("supplier", "Supplier name *", False, None),
            ("qty", "Quantity received *", False, None),
            ("price", "Purchase price per unit (₹) *", False, None),
            ("batch", "Batch number (optional)", False, None),
            ("expiry", "Expiry date (YYYY-MM-DD)", False, None),
            ("invoice", "Invoice number (optional)", False, None),
        ]

        for key, label, is_combo, values in placeholders:
            if is_combo:
                w = ctk.CTkComboBox(dialog, values=values, width=340,
                                   font=ctk.CTkFont(size=13))
                w.set("Select product")
            else:
                w = ctk.CTkEntry(dialog, placeholder_text=label,
                                width=340, font=ctk.CTkFont(size=13))
            w.pack(pady=5)
            fields[key] = w

        error_label = ctk.CTkLabel(dialog, text="", text_color="red")
        error_label.pack(pady=4)

        def save():
            product_name = fields["product"].get()
            supplier = fields["supplier"].get().strip()
            qty = fields["qty"].get().strip()
            price = fields["price"].get().strip()

            if product_name == "Select product" or not supplier or not qty or not price:
                error_label.configure(text="Fill all required (*) fields.")
                return
            try:
                qty_f = float(qty)
                price_f = float(price)
            except ValueError:
                error_label.configure(text="Qty and Price must be numbers.")
                return

            product = product_map[product_name]
            add_inward_stock(
                product["product_id"], supplier, qty_f, price_f,
                fields["batch"].get().strip(),
                fields["expiry"].get().strip(),
                fields["invoice"].get().strip(),
                "", self.user["user_id"])
            messagebox.showinfo("Success", "Stock entry added!")
            dialog.destroy()
            self.refresh_table()

        ctk.CTkButton(dialog, text="✅ Save Entry", width=340,
                     font=ctk.CTkFont(size=13, weight="bold"),
                     command=save).pack(pady=16)