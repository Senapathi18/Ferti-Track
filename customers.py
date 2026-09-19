# modules/customers.py — Fixed: add button visible, location working
import customtkinter as ctk
from tkinter import messagebox
from database import (add_customer, get_all_customers,
                      get_customer_purchase_history,
                      delete_customer, get_all_districts,
                      get_mandals_for_district,
                      get_villages_for_mandal,
                      search_villages_db, add_village)

N  = "#1e3a5f"
B  = "#2563eb"
BD = "#1d4ed8"
W  = "#ffffff"
G5 = "#f8fafc"
G2 = "#e2e8f0"
G8 = "#1e293b"
R  = "#dc2626"


def F(size=13, bold=False):
    return ctk.CTkFont(
        family="Segoe UI", size=size,
        weight="bold" if bold else "normal")


class CustomersScreen(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color="#f1f5f9")
        self.pack(fill="both", expand=True)
        self.user = user
        self._build()

    def _build(self):
        # ── HEADER (always visible at top) ──────────
        hdr = ctk.CTkFrame(self, fg_color=W, height=64)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        ctk.CTkLabel(
            hdr, text="👥  Customers",
            font=F(20, True), text_color=G8
        ).pack(side="left", padx=24, pady=16)

        # ADD BUTTON — always on the right of header
        ctk.CTkButton(
            hdr, text="+ Add Customer",
            font=F(13, True),
            fg_color=B, hover_color=BD,
            height=36, corner_radius=8,
            command=self.open_add_dialog
        ).pack(side="right", padx=24, pady=14)

        # ── SCROLLABLE TABLE ─────────────────────────
        self.tbl = ctk.CTkScrollableFrame(self, fg_color="#f1f5f9")
        self.tbl.pack(fill="both", expand=True, padx=20, pady=12)

        self.refresh_table()

    def refresh_table(self):
        for w in self.tbl.winfo_children():
            w.destroy()

        cols   = ["Name", "Phone", "Location", "District", "Actions"]
        widths = [160, 120, 200, 140, 180]

        hr = ctk.CTkFrame(self.tbl, fg_color=N, height=40)
        hr.pack(fill="x", pady=(0, 2))
        hr.pack_propagate(False)
        for i, (c, w) in enumerate(zip(cols, widths)):
            ctk.CTkLabel(hr, text=c, width=w, anchor="w",
                         font=F(11, True),
                         text_color=W).grid(
                row=0, column=i, padx=8, pady=8)

        rows = get_all_customers()
        if not rows:
            ctk.CTkLabel(self.tbl,
                         text="No customers yet.\n"
                              "Click '+ Add Customer' button above to add one.",
                         text_color="#94a3b8",
                         font=F(13),
                         justify="center").pack(pady=60)
            return

        for i, c in enumerate(rows):
            c   = dict(c)
            bg  = G5 if i % 2 else W
            row = ctk.CTkFrame(self.tbl, fg_color=bg, corner_radius=0)
            row.pack(fill="x", pady=1)

            for j, (val, w) in enumerate(zip([
                c["name"],
                c["phone"] or "-",
                c["village"] or "-",
                c["district"] or "-",
            ], widths)):
                ctk.CTkLabel(row, text=val, width=w, anchor="w",
                             font=F(12), text_color=G8).grid(
                    row=0, column=j, padx=8, pady=8)

            # Action buttons
            acts = ctk.CTkFrame(row, fg_color="transparent")
            acts.grid(row=0, column=4, padx=8, pady=4)

            ctk.CTkButton(
                acts, text="History", width=90, height=30,
                fg_color="#dbeafe", hover_color=B,
                text_color=B, font=F(11),
                corner_radius=6,
                command=lambda cid=c["customer_id"]:
                self.view_history(cid)
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                acts, text="Delete", width=80, height=30,
                fg_color="#fee2e2", hover_color=R,
                text_color=R, font=F(11),
                corner_radius=6,
                command=lambda cid=c["customer_id"],
                nm=c["name"]: self.confirm_delete(cid, nm)
            ).pack(side="left", padx=2)

    def confirm_delete(self, cid, name):
        if messagebox.askyesno(
                "Delete Customer",
                f"Remove '{name}'?\n"
                "Past sales will be kept but unlinked."):
            delete_customer(cid)
            messagebox.showinfo("Done", f"'{name}' removed.")
            self.refresh_table()

    def view_history(self, cid):
        h = get_customer_purchase_history(cid)
        win = ctk.CTkToplevel(self)
        win.title("Purchase History")
        win.geometry("500x420")
        win.grab_set()

        ctk.CTkLabel(win, text="Purchase History",
                     font=F(16, True)).pack(pady=12)

        if not h:
            ctk.CTkLabel(win, text="No purchases yet.",
                         text_color="#94a3b8").pack(pady=20)
            return

        s = ctk.CTkScrollableFrame(win)
        s.pack(fill="both", expand=True, padx=12, pady=12)
        for r in h:
            r = dict(r)
            ctk.CTkLabel(s,
                         text=f"#{r['sale_id']}  •  "
                              f"Rs.{r['final_amount']:.2f}  •  "
                              f"{r['payment_status']}  •  "
                              f"{str(r['sale_date'])[:10]}",
                         anchor="w", font=F(12)).pack(
                fill="x", pady=4, padx=8)

    def open_add_dialog(self):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Add New Customer")
        dlg.geometry("460x650")
        dlg.grab_set()
        dlg.resizable(False, True)
        dlg.configure(fg_color="#f1f5f9")

        # Dialog header
        hdr = ctk.CTkFrame(dlg, fg_color=N, height=56)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="👥  Add New Customer",
                     font=F(15, True),
                     text_color=W).pack(side="left",
                                        padx=20, pady=14)

        # ── FIXED FOOTER (always visible, packed BEFORE body) ──
        footer = ctk.CTkFrame(dlg, fg_color="#f1f5f9", height=70)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        err_lbl = ctk.CTkLabel(
            footer, text="", text_color=R, font=F(11))
        err_lbl.pack(anchor="w", padx=24, pady=(6, 0))

        save_btn = ctk.CTkButton(
            footer, text="Save Customer",
            width=380, height=42,
            fg_color=B, hover_color=BD,
            font=F(14, True), corner_radius=8)
        save_btn.pack(padx=24, pady=(4, 12))

        # ── SCROLLABLE BODY (fills remaining space above footer) ──
        body = ctk.CTkScrollableFrame(dlg, fg_color="#f1f5f9")
        body.pack(fill="both", expand=True, side="top", padx=24, pady=(16, 0))

        def lbl(text):
            ctk.CTkLabel(body, text=text,
                         font=F(11, True),
                         text_color="#475569").pack(
                anchor="w", pady=(10, 2))

        lbl("Customer Name *")
        name_e = ctk.CTkEntry(
            body, placeholder_text="e.g. Ramesh Kumar",
            width=380, font=F(13), height=38, corner_radius=8,
            fg_color=W, border_color=G2)
        name_e.pack(anchor="w")

        lbl("Phone Number")
        phone_e = ctk.CTkEntry(
            body, placeholder_text="10-digit mobile number",
            width=380, font=F(13), height=38, corner_radius=8,
            fg_color=W, border_color=G2)
        phone_e.pack(anchor="w")

        # Location — State fixed
        ctk.CTkLabel(body, text="State",
                     font=F(11, True),
                     text_color="#475569").pack(
            anchor="w", pady=(10, 2))
        ctk.CTkLabel(body, text="Andhra Pradesh  ✅",
                     font=F(12, True),
                     text_color="#059669").pack(anchor="w")

        # District
        lbl("District *")
        districts = get_all_districts()
        if not districts:
            districts = ["Run populate_villages.py first"]

        dist_var = ctk.StringVar(value="Select District")
        dist_dd = ctk.CTkComboBox(
            body, values=districts, width=380,
            font=F(13), height=38, corner_radius=8,
            variable=dist_var,
            command=lambda ch: _on_district(ch))
        dist_dd.pack(anchor="w")

        # Mandal
        lbl("Mandal *")
        mandal_dd = ctk.CTkComboBox(
            body, values=["Select district first"],
            width=380, font=F(13), height=38, corner_radius=8,
            command=lambda ch: _on_mandal(ch))
        mandal_dd.pack(anchor="w")

        # Village search
        lbl("Village / Town *  (type to search)")
        village_frame = ctk.CTkFrame(body, fg_color="transparent")
        village_frame.pack(anchor="w")

        village_e = ctk.CTkEntry(
            village_frame,
            placeholder_text="Type village name to search...",
            width=316, font=F(13), height=38, corner_radius=8,
            fg_color=W, border_color=G2)
        village_e.pack(side="left")
        village_e.bind("<KeyRelease>", lambda e: _search_village())

        ctk.CTkButton(
            village_frame, text="+ Add", width=58, height=38,
            fg_color="#059669", hover_color="#047857",
            font=F(11, True), corner_radius=8,
            command=lambda: _add_new_village()
        ).pack(side="left", padx=(6, 0))

        # Suggestion list
        suggest_frame = ctk.CTkScrollableFrame(
            body, fg_color=W, height=0,
            border_width=1, border_color=G2)
        suggest_frame.pack(anchor="w", fill="x")

        lbl("Notes (optional)")
        notes_e = ctk.CTkEntry(
            body, placeholder_text="Any notes about this customer",
            width=380, font=F(13), height=38, corner_radius=8,
            fg_color=W, border_color=G2)
        notes_e.pack(anchor="w", pady=(0, 16))

        # State variables
        _state = {"district": "", "mandal": ""}

        def _on_district(choice):
            _state["district"] = choice
            _state["mandal"]   = ""
            mandals = get_mandals_for_district(choice)
            if mandals:
                mandal_dd.configure(values=mandals)
                mandal_dd.set("Select Mandal")
            else:
                mandal_dd.configure(values=["No mandals found"])
                mandal_dd.set("No mandals found")
            village_e.delete(0, "end")
            _hide_suggestions()

        def _on_mandal(choice):
            _state["mandal"] = choice
            village_e.delete(0, "end")
            villages = get_villages_for_mandal(
                _state["district"], choice)
            village_e.configure(
                placeholder_text=f"{len(villages)} villages — type to filter")
            _hide_suggestions()

        def _search_village():
            q = village_e.get().strip()
            if not _state["district"] or not _state["mandal"]:
                return
            if len(q) < 1:
                _hide_suggestions()
                return
            matches = search_villages_db(
                _state["district"], _state["mandal"], q)
            _show_suggestions(matches)

        def _show_suggestions(villages):
            for w in suggest_frame.winfo_children():
                w.destroy()
            if not villages:
                suggest_frame.configure(height=36)
                ctk.CTkLabel(suggest_frame,
                             text="No match — type name and click + Add",
                             text_color="#94a3b8",
                             font=F(11)).pack(padx=8, pady=4)
            else:
                suggest_frame.configure(
                    height=min(len(villages), 6) * 34)
                for v in villages[:6]:
                    ctk.CTkButton(
                        suggest_frame, text=v, anchor="w",
                        fg_color="transparent",
                        text_color=G8,
                        hover_color="#dbeafe", height=30,
                        font=F(12),
                        command=lambda vv=v: _pick_village(vv)
                    ).pack(fill="x", padx=4, pady=1)

        def _hide_suggestions():
            for w in suggest_frame.winfo_children():
                w.destroy()
            suggest_frame.configure(height=0)

        def _pick_village(v):
            village_e.delete(0, "end")
            village_e.insert(0, v)
            _hide_suggestions()

        def _add_new_village():
            v = village_e.get().strip()
            d = _state["district"]
            m = _state["mandal"]
            if not v or not d or not m:
                err_lbl.configure(
                    text="Select district and mandal first.")
                return
            add_village(d, m, v)
            err_lbl.configure(
                text=f"✅ '{v}' added to {m}",
                text_color="#059669")

        def save():
            name    = name_e.get().strip()
            phone   = phone_e.get().strip()
            dist    = dist_dd.get()
            mandal  = mandal_dd.get()
            village = village_e.get().strip()

            if not name:
                err_lbl.configure(text="Name is required.", text_color=R)
                return
            if phone and (not phone.isdigit() or len(phone) != 10):
                err_lbl.configure(text="Phone must be 10 digits.", text_color=R)
                return
            if dist == "Select District":
                err_lbl.configure(text="Please select a district.", text_color=R)
                return
            if not village:
                err_lbl.configure(text="Please enter a village name.", text_color=R)
                return

            full_loc = f"{village}, {mandal}"
            add_customer(name, phone, full_loc,
                         dist, notes_e.get().strip())
            messagebox.showinfo("Success",
                                f"Customer '{name}' added!")
            dlg.destroy()
            self.refresh_table()

        save_btn.configure(command=save)