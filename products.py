# modules/products.py
import customtkinter as ctk
from tkinter import messagebox
from database import add_product, get_all_products, get_current_stock, delete_product
from config import PRODUCT_CATEGORIES, PRODUCT_UNITS, HSN_GST_MAP

N  = "#1e3a5f"   # Navy       – header bars, sidebar
B  = "#2563eb"   # Blue       – primary buttons, links
BD = "#1d4ed8"   # Blue Dark  – button hover state
W  = "#ffffff"   # White      – card/dialog backgrounds
G5 = "#f8fafc"   # Gray 50    – alternating row background
G2 = "#e2e8f0"   # Gray 200   – borders, entry outlines
G8 = "#1e293b"   # Gray 800   – primary text color
R  = "#dc2626"   # Red        – delete actions, error text


def F(size=13, bold=False):
    return ctk.CTkFont(
        family="Segoe UI", size=size,
        weight="bold" if bold else "normal")


class ProductsScreen(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color="#f1f5f9")
        self.pack(fill="both", expand=True)
        self.user = user

        # ── HEADER ──────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=W, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="📦  Products",
            font=F(20, True),
            text_color="#0f172a"
        ).pack(side="left", padx=24, pady=16)

        ctk.CTkButton(
            header, text="+ Add Product",
            font=F(13, True),
            fg_color=B, hover_color=BD,
            height=36, corner_radius=8,
            command=self.open_add_dialog
        ).pack(side="right", padx=24, pady=14)

        # ── TABLE ────────────────────────────────────
        self.table_frame = ctk.CTkScrollableFrame(
            self, fg_color="#f1f5f9")
        self.table_frame.pack(
            fill="both", expand=True, padx=20, pady=12)

        self.refresh_table()

    def refresh_table(self):
        for w in self.table_frame.winfo_children():
            w.destroy()

        # Column headers
        headers = ["Product Name", "Category", "Unit",
                   "HSN Code", "GST %", "Price (₹)", "Stock", "Action"]
        widths  = [160, 120, 80, 100, 60, 100, 100, 100]

        hr = ctk.CTkFrame(self.table_frame, fg_color=N, height=40)
        hr.pack(fill="x", pady=(0, 2))
        hr.pack_propagate(False)
        for i, (h, w) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(
                hr, text=h, width=w, anchor="w",
                font=F(11, True),
                text_color=W
            ).grid(row=0, column=i, padx=8, pady=8)

        # Rows
        all_products = get_all_products()
        if not all_products:
            ctk.CTkLabel(
                self.table_frame,
                text="No products yet. Click '+ Add Product' to get started.",
                font=F(13),
                text_color="#94a3b8"
            ).pack(pady=60)
            return

        for idx, p in enumerate(all_products):
            p = dict(p)
            stock = get_current_stock(p["product_id"])
            stock_color = R if stock <= p["min_stock"] else "#059669"
            bg = G5 if idx % 2 == 0 else W

            row = ctk.CTkFrame(
                self.table_frame, fg_color=bg, corner_radius=0)
            row.pack(fill="x", pady=1)

            values = [
                p["product_name"],
                p["category"],
                p["unit"],
                p.get("hsn_code") or "-",
                f"{p.get('gst_rate', 5):.0f}%",
                f"₹{p['current_price']:.2f}",
            ]
            for i, (val, w) in enumerate(zip(values, widths)):
                ctk.CTkLabel(
                    row, text=val, width=w, anchor="w",
                    font=F(12),
                    text_color=G8
                ).grid(row=0, column=i, padx=8, pady=7)

            # Stock column with color
            ctk.CTkLabel(
                row,
                text=f"{stock} {p['unit']}",
                width=widths[6], anchor="w",
                font=F(12, True),
                text_color=stock_color
            ).grid(row=0, column=6, padx=8, pady=7)

            # Delete button
            ctk.CTkButton(
                row, text="Delete", width=90, height=28,
                fg_color="#fee2e2", hover_color=R,
                text_color=R,
                font=F(11),
                corner_radius=6,
                command=lambda pid=p["product_id"],
                name=p["product_name"]: self.confirm_delete(pid, name)
            ).grid(row=0, column=7, padx=8, pady=4)

    def confirm_delete(self, product_id, name):
        if messagebox.askyesno(
                "Delete Product",
                f"Hide '{name}' from the product list?\n\n"
                "All stock history will be kept for records."):
            delete_product(product_id)
            messagebox.showinfo("Done", f"'{name}' has been removed.")
            self.refresh_table()

    def open_add_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Product")
        dialog.geometry("460x600")
        dialog.grab_set()
        dialog.resizable(False, True)
        dialog.configure(fg_color="#f1f5f9")

        # Dialog header
        hdr = ctk.CTkFrame(dialog, fg_color=N, height=56)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
        ctk.CTkLabel(
            hdr, text="📦  Add New Product",
            font=F(15, True),
            text_color=W
        ).pack(side="left", padx=20, pady=14)

        # ── FIXED FOOTER (always visible, packed BEFORE body) ──
        footer = ctk.CTkFrame(dialog, fg_color="#f1f5f9", height=70)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self._dlg_error = ctk.CTkLabel(
            footer, text="", text_color=R,
            font=F(11))
        self._dlg_error.pack(anchor="w", padx=24, pady=(6, 0))

        ctk.CTkButton(
            footer, text="Save Product", width=380, height=40,
            fg_color=B, hover_color=BD,
            font=F(13, True),
            corner_radius=8, command=self._save_product
        ).pack(padx=24, pady=(4, 12))

        # ── SCROLLABLE BODY (fills remaining space above footer) ──
        body = ctk.CTkScrollableFrame(dialog, fg_color="#f1f5f9")
        body.pack(fill="both", expand=True, side="top", padx=24, pady=(16, 0))

        def lbl(text):
            ctk.CTkLabel(
                body, text=text,
                font=F(11, True),
                text_color="#475569"
            ).pack(anchor="w", pady=(8, 2))

        lbl("Product Name *")
        self._dlg_name = ctk.CTkEntry(
            body, placeholder_text="e.g. Urea 50kg", width=380,
            font=F(13), height=38, corner_radius=8)
        self._dlg_name.pack(anchor="w")

        lbl("Category *")
        self._dlg_category = ctk.CTkComboBox(
            body, values=PRODUCT_CATEGORIES, width=380,
            font=F(13), height=38, corner_radius=8,
            command=self._on_category_change)
        self._dlg_category.set("Select category")
        self._dlg_category.pack(anchor="w")

        lbl("Unit *")
        self._dlg_unit = ctk.CTkComboBox(
            body, values=PRODUCT_UNITS, width=380,
            font=F(13), height=38, corner_radius=8)
        self._dlg_unit.set("Select unit")
        self._dlg_unit.pack(anchor="w")

        lbl("Price per unit (₹) *")
        self._dlg_price = ctk.CTkEntry(
            body, placeholder_text="e.g. 280", width=380,
            font=F(13), height=38, corner_radius=8)
        self._dlg_price.pack(anchor="w")

        lbl("Minimum Stock Alert Level")
        self._dlg_min = ctk.CTkEntry(
            body, placeholder_text="e.g. 10", width=380,
            font=F(13), height=38, corner_radius=8)
        self._dlg_min.pack(anchor="w")

        lbl("HSN Code (auto-filled)")
        self._dlg_hsn = ctk.CTkEntry(
            body, placeholder_text="Auto-filled when category selected",
            width=380, font=F(13), height=38, corner_radius=8)
        self._dlg_hsn.pack(anchor="w")

        self._dlg_gst = ctk.CTkLabel(
            body, text="GST Rate: select a category first",
            font=F(11, True),
            text_color=B)
        self._dlg_gst.pack(anchor="w", pady=(4, 16))

        self._active_dialog = dialog

    def _on_category_change(self, choice):
        if choice in HSN_GST_MAP:
            hsn, gst = HSN_GST_MAP[choice]
            self._dlg_hsn.delete(0, "end")
            self._dlg_hsn.insert(0, hsn)
            self._dlg_gst.configure(
                text=f"GST Rate: {gst}%  ✅",
                text_color="#059669")

    def _save_product(self):
        name     = self._dlg_name.get().strip()
        category = self._dlg_category.get()
        unit     = self._dlg_unit.get()
        price    = self._dlg_price.get().strip()
        min_s    = self._dlg_min.get().strip() or "0"
        hsn      = self._dlg_hsn.get().strip()
        gst      = HSN_GST_MAP.get(category, ("", 5))[1]

        if not name:
            self._dlg_error.configure(text="⚠️ Product name is required.")
            return
        if category == "Select category":
            self._dlg_error.configure(text="⚠️ Please select a category.")
            return
        if unit == "Select unit":
            self._dlg_error.configure(text="⚠️ Please select a unit.")
            return
        if not price:
            self._dlg_error.configure(text="⚠️ Price is required.")
            return
        try:
            price_f = float(price)
            min_f   = float(min_s)
        except ValueError:
            self._dlg_error.configure(
                text="⚠️ Price and min stock must be numbers.")
            return

        add_product(name, category, unit, price_f, min_f, "", hsn, gst)
        messagebox.showinfo("Success", f"'{name}' added successfully!")
        self._active_dialog.destroy()
        self.refresh_table()