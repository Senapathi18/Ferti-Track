# modules/outward.py

import customtkinter as ctk
from tkinter import messagebox
import os
from database import (add_sale, get_all_products, get_sales_report,
                      get_current_stock, get_all_customers, delete_sale)
try:
    from modules.invoice import generate_invoice_pdf
    INVOICE_AVAILABLE = True
except Exception:
    INVOICE_AVAILABLE = False


class OutwardScreen(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color="white")
        self.pack(fill="both", expand=True)
        self.user = user
        self.cart = []

        header = ctk.CTkFrame(self, fg_color="white")
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(header, text="⬆️ Outward Stock / Sales",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color="#1a1a1a").pack(side="left")
        ctk.CTkButton(header, text="+ New Sale",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     command=self.open_sale_dialog).pack(side="right")

        self.table_frame = ctk.CTkScrollableFrame(self, fg_color="white")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.refresh_table()

    def refresh_table(self):
        for w in self.table_frame.winfo_children():
            w.destroy()

        headers = ["Sale #", "Customer", "Amount (₹)",
                   "Payment", "Status", "Date", "Invoice", "Delete"]
        hr = ctk.CTkFrame(self.table_frame, fg_color="#f0f4f8")
        hr.pack(fill="x", pady=(0, 4))
        for i, h in enumerate(headers):
            ctk.CTkLabel(hr, text=h,
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="#1a1a1a", width=100, anchor="w").grid(
                row=0, column=i, padx=6, pady=8)

        sales = get_sales_report()
        if not sales:
            ctk.CTkLabel(self.table_frame,
                        text="No sales recorded yet. Click '+ New Sale' to start.",
                        text_color="gray",
                        font=ctk.CTkFont(size=13)).pack(pady=40)
            return

        for s in sales:
            s = dict(s)
            row = ctk.CTkFrame(self.table_frame, fg_color="white",
                              border_width=1, border_color="#eee")
            row.pack(fill="x", pady=2)

            for i, val in enumerate([
                f"#{s['sale_id']}",
                s["customer_name"] or "Walk-in",
                f"₹{s['final_amount']:.2f}",
                s["payment_mode"],
                s["payment_status"],
                str(s["sale_date"])[:10],
            ]):
                color = "#e74c3c" if (
                    i == 4 and s["payment_status"] == "Credit") else "#1a1a1a"
                ctk.CTkLabel(row, text=val, width=100, anchor="w",
                            font=ctk.CTkFont(size=12),
                            text_color=color).grid(
                    row=0, column=i, padx=6, pady=8)

            # PDF button
            ctk.CTkButton(
                row, text="📄 PDF", width=70,
                fg_color="#0f6e56", hover_color="#0a5443",
                font=ctk.CTkFont(size=11),
                command=lambda sid=s["sale_id"]: self.download_invoice(sid)
            ).grid(row=0, column=6, padx=4, pady=4)

            # Delete button
            ctk.CTkButton(
                row, text="🗑️", width=44,
                fg_color="#e74c3c", hover_color="#c0392b",
                font=ctk.CTkFont(size=12),
                command=lambda sid=s["sale_id"]: self.confirm_delete(sid)
            ).grid(row=0, column=7, padx=4, pady=4)

    def confirm_delete(self, sale_id):
        if messagebox.askyesno(
                "Delete Sale",
                f"Delete Sale #{sale_id}?\n\n"
                "⚠️ This will also remove all stock movements for this sale."):
            delete_sale(sale_id)
            messagebox.showinfo("Deleted", f"Sale #{sale_id} deleted.")
            self.refresh_table()

    def download_invoice(self, sale_id):
        if not INVOICE_AVAILABLE:
            messagebox.showwarning("Invoice", "Invoice module not available.")
            return
        try:
            path = generate_invoice_pdf(sale_id)
            full_path = os.path.abspath(path)
            messagebox.showinfo("Invoice Ready", f"Saved at:\n{full_path}")
            os.startfile(full_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate invoice:\n{e}")

    def open_sale_dialog(self):
        products = get_all_products()
        if not products:
            messagebox.showwarning("No Products",
                                   "Add products before creating a sale.")
            return

        product_names = [p["product_name"] for p in products]
        product_map = {p["product_name"]: dict(p) for p in products}
        customers = get_all_customers()
        customer_names = ["Walk-in Customer"] + [c["name"] for c in customers]
        customer_map = {c["name"]: c["customer_id"] for c in customers}
        self.cart = []

        dialog = ctk.CTkToplevel(self)
        dialog.title("New Sale")
        dialog.geometry("480x660")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="🛒 New Sale",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(16, 4))

        # Customer
        ctk.CTkLabel(dialog, text="Customer",
                     font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w", padx=20)
        customer_dd = ctk.CTkComboBox(dialog, values=customer_names,
                                      width=420, font=ctk.CTkFont(size=13))
        customer_dd.set("Walk-in Customer")
        customer_dd.pack(pady=(2, 10), padx=20)

        # Item entry row
        ctk.CTkLabel(dialog, text="Add items to cart",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#0f6e56").pack(anchor="w", padx=20)

        item_row = ctk.CTkFrame(dialog, fg_color="#f7f7f7")
        item_row.pack(fill="x", padx=20, pady=4)

        prod_dd = ctk.CTkComboBox(item_row, values=product_names,
                                  width=180, font=ctk.CTkFont(size=12))
        prod_dd.set("Select product")
        prod_dd.grid(row=0, column=0, padx=4, pady=8)

        qty_e = ctk.CTkEntry(item_row, placeholder_text="Qty",
                             width=70, font=ctk.CTkFont(size=12))
        qty_e.grid(row=0, column=1, padx=4)

        price_e = ctk.CTkEntry(item_row, placeholder_text="Price ₹",
                               width=80, font=ctk.CTkFont(size=12))
        price_e.grid(row=0, column=2, padx=4)

        # Cart display
        cart_label = ctk.CTkLabel(dialog,
                                  text="Cart is empty — add items above",
                                  text_color="gray", justify="left", anchor="w",
                                  font=ctk.CTkFont(size=12))
        cart_label.pack(fill="x", padx=20, pady=4)

        def update_cart_display():
            if not self.cart:
                cart_label.configure(text="Cart is empty", text_color="gray")
                return
            lines = []
            total = 0
            for item in self.cart:
                lt = item["qty"] * item["price"]
                total += lt
                lines.append(
                    f"✅ {item['name']}  ×{item['qty']}  "
                    f"@ ₹{item['price']}  = ₹{lt:.2f}")
            lines.append(f"\n── Subtotal: ₹{total:.2f}")
            cart_label.configure(text="\n".join(lines), text_color="#1a1a1a")

        def add_to_cart():
            name = prod_dd.get()
            qty = qty_e.get().strip()
            price = price_e.get().strip()
            if name == "Select product" or not qty or not price:
                messagebox.showwarning("Missing", "Select product, qty and price.")
                return
            try:
                qty_f = float(qty)
                price_f = float(price)
            except ValueError:
                messagebox.showwarning("Invalid", "Qty and price must be numbers.")
                return
            product = product_map[name]
            available = get_current_stock(product["product_id"])
            already = sum(i["qty"] for i in self.cart
                         if i["product_id"] == product["product_id"])
            if qty_f + already > available:
                messagebox.showwarning(
                    "Stock",
                    f"Only {available} {product['unit']} available.")
                return
            self.cart.append({
                "product_id": product["product_id"],
                "name": name, "qty": qty_f, "price": price_f})
            update_cart_display()
            qty_e.delete(0, "end")
            price_e.delete(0, "end")

        ctk.CTkButton(item_row, text="+ Add", width=80,
                     fg_color="#0f6e56", hover_color="#0a5443",
                     font=ctk.CTkFont(size=12),
                     command=add_to_cart).grid(row=0, column=3, padx=4)

        # Discount & Payment
        ctk.CTkLabel(dialog, text="Discount (₹)",
                     font=ctk.CTkFont(size=11), text_color="gray").pack(
            anchor="w", padx=20, pady=(8, 0))
        discount_e = ctk.CTkEntry(dialog, placeholder_text="0",
                                  width=420, font=ctk.CTkFont(size=13))
        discount_e.pack(padx=20, pady=(2, 6))

        ctk.CTkLabel(dialog, text="Payment Mode",
                     font=ctk.CTkFont(size=11), text_color="gray").pack(
            anchor="w", padx=20)
        payment_dd = ctk.CTkComboBox(
            dialog, values=["Cash", "UPI", "Credit", "Cheque", "Kisan Credit Card"],
            width=420, font=ctk.CTkFont(size=13))
        payment_dd.set("Cash")
        payment_dd.pack(padx=20, pady=(2, 6))

        error_label = ctk.CTkLabel(dialog, text="", text_color="red")
        error_label.pack(pady=4)

        def complete_sale():
            if not self.cart:
                error_label.configure(text="Add at least one item to cart.")
                return
            customer_name = customer_dd.get()
            customer_id = customer_map.get(customer_name)
            try:
                discount = float(discount_e.get().strip() or "0")
            except ValueError:
                error_label.configure(text="Discount must be a number.")
                return
            items = [{"product_id": i["product_id"],
                     "qty": i["qty"], "price": i["price"]}
                    for i in self.cart]
            sale_id = add_sale(
                customer_id, items, discount=discount,
                payment_mode=payment_dd.get(),
                user_id=self.user["user_id"])
            messagebox.showinfo("Success", f"Sale #{sale_id} recorded!")
            dialog.destroy()
            self.refresh_table()
            if INVOICE_AVAILABLE:
                self.download_invoice(sale_id)

        ctk.CTkButton(dialog, text="✅ Complete Sale & Print Invoice",
                     width=420, fg_color="#0f6e56", hover_color="#0a5443",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     command=complete_sale).pack(pady=16)