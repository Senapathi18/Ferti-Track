# modules/settings.py — User management, audit log, change password (admin only)

import customtkinter as ctk
from tkinter import messagebox
from database import (get_all_users, create_user, toggle_user_active,
                      get_audit_log, change_password, verify_current_password)


class SettingsScreen(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color="white")
        self.pack(fill="both", expand=True)
        self.user = user

        ctk.CTkLabel(self, text="⚙️ Settings",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=20, pady=(20, 10))

        tabs = ctk.CTkTabview(self, width=900, height=550)
        tabs.pack(fill="both", expand=True, padx=20, pady=10)

        # Tab order depends on role
        if user["role"] == "admin":
            tabs.add("Staff Accounts")
            tabs.add("Audit Log")
        tabs.add("Change Password")

        if user["role"] == "admin":
            self.build_staff_tab(tabs.tab("Staff Accounts"))
            self.build_audit_tab(tabs.tab("Audit Log"))
        self.build_password_tab(tabs.tab("Change Password"))

    # ── STAFF ACCOUNTS TAB (admin only) ──────────────────
    def build_staff_tab(self, tab):
        ctk.CTkButton(tab, text="+ Add Staff Account",
                     command=self.open_add_user_dialog).pack(anchor="w", pady=10)

        self.users_frame = ctk.CTkScrollableFrame(tab, fg_color="white")
        self.users_frame.pack(fill="both", expand=True)
        self.refresh_users()

    def refresh_users(self):
        for widget in self.users_frame.winfo_children():
            widget.destroy()

        headers = ["Username", "Full Name", "Role", "Status", "Action"]
        header_row = ctk.CTkFrame(self.users_frame, fg_color="#f0f4f8")
        header_row.pack(fill="x", pady=(0, 4))
        for i, h in enumerate(headers):
            ctk.CTkLabel(header_row, text=h, font=ctk.CTkFont(weight="bold"),
                        width=140, anchor="w").grid(row=0, column=i, padx=8, pady=8)

        for u in get_all_users():
            row = ctk.CTkFrame(self.users_frame, fg_color="white",
                              border_width=1, border_color="#eee")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=u["username"], width=140, anchor="w").grid(
                row=0, column=0, padx=8, pady=8)
            ctk.CTkLabel(row, text=u["full_name"], width=140, anchor="w").grid(
                row=0, column=1, padx=8, pady=8)
            ctk.CTkLabel(row, text=u["role"], width=140, anchor="w").grid(
                row=0, column=2, padx=8, pady=8)
            status = "Active" if u["is_active"] else "Disabled"
            color = "green" if u["is_active"] else "red"
            ctk.CTkLabel(row, text=status, width=140, anchor="w", text_color=color).grid(
                row=0, column=3, padx=8, pady=8)

            if u["username"] != "admin":   # protect the default admin account
                action_text = "Disable" if u["is_active"] else "Enable"
                ctk.CTkButton(row, text=action_text, width=100,
                            command=lambda uid=u["user_id"], active=u["is_active"]:
                            self.toggle_user(uid, active)).grid(row=0, column=4, padx=8, pady=4)

    def toggle_user(self, user_id, currently_active):
        toggle_user_active(user_id, 0 if currently_active else 1)
        self.refresh_users()

    def open_add_user_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Staff Account")
        dialog.geometry("360x380")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Add Staff Account",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))

        username_entry = ctk.CTkEntry(dialog, placeholder_text="Username", width=280)
        username_entry.pack(pady=6)

        fullname_entry = ctk.CTkEntry(dialog, placeholder_text="Full name", width=280)
        fullname_entry.pack(pady=6)

        password_entry = ctk.CTkEntry(dialog, placeholder_text="Password", show="*", width=280)
        password_entry.pack(pady=6)

        role_dropdown = ctk.CTkComboBox(dialog, values=["staff", "admin"], width=280)
        role_dropdown.pack(pady=6)
        role_dropdown.set("staff")

        error_label = ctk.CTkLabel(dialog, text="", text_color="red")
        error_label.pack(pady=4)

        def save():
            username = username_entry.get().strip()
            full_name = fullname_entry.get().strip()
            password = password_entry.get().strip()
            role = role_dropdown.get()

            if not username or not full_name or not password:
                error_label.configure(text="All fields are required.")
                return
            if len(password) < 6:
                error_label.configure(text="Password must be at least 6 characters.")
                return

            success, msg = create_user(username, password, full_name, role)
            if not success:
                error_label.configure(text=msg)
                return

            messagebox.showinfo("Success", f"Account '{username}' created!")
            dialog.destroy()
            self.refresh_users()

        ctk.CTkButton(dialog, text="Create Account", width=280,
                     command=save).pack(pady=16)

    # ── AUDIT LOG TAB (admin only) ──────────────────
    def build_audit_tab(self, tab):
        log_frame = ctk.CTkScrollableFrame(tab, fg_color="white")
        log_frame.pack(fill="both", expand=True, pady=10)

        headers = ["Time", "User", "Action", "Details"]
        header_row = ctk.CTkFrame(log_frame, fg_color="#f0f4f8")
        header_row.pack(fill="x", pady=(0, 4))
        for i, h in enumerate(headers):
            ctk.CTkLabel(header_row, text=h, font=ctk.CTkFont(weight="bold"),
                        width=180, anchor="w").grid(row=0, column=i, padx=8, pady=8)

        for log in get_audit_log():
            row = ctk.CTkFrame(log_frame, fg_color="white",
                              border_width=1, border_color="#eee")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=str(log["timestamp"])[:16], width=180, anchor="w").grid(
                row=0, column=0, padx=8, pady=6)
            ctk.CTkLabel(row, text=log["username"] or "Unknown", width=180, anchor="w").grid(
                row=0, column=1, padx=8, pady=6)
            ctk.CTkLabel(row, text=log["action"], width=180, anchor="w").grid(
                row=0, column=2, padx=8, pady=6)
            ctk.CTkLabel(row, text=log["details"] or "-", width=180, anchor="w").grid(
                row=0, column=3, padx=8, pady=6)

    # ── CHANGE PASSWORD TAB (everyone) ──────────────────
    def build_password_tab(self, tab):
        frame = ctk.CTkFrame(tab, fg_color="white")
        frame.pack(pady=30)

        ctk.CTkLabel(frame, text="Change Your Password",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 16))

        current_entry = ctk.CTkEntry(frame, placeholder_text="Current password", show="*", width=300)
        current_entry.pack(pady=6)

        new_entry = ctk.CTkEntry(frame, placeholder_text="New password", show="*", width=300)
        new_entry.pack(pady=6)

        confirm_entry = ctk.CTkEntry(frame, placeholder_text="Confirm new password", show="*", width=300)
        confirm_entry.pack(pady=6)

        error_label = ctk.CTkLabel(frame, text="", text_color="red")
        error_label.pack(pady=4)

        def update_password():
            current = current_entry.get().strip()
            new = new_entry.get().strip()
            confirm = confirm_entry.get().strip()

            if not verify_current_password(self.user["user_id"], current):
                error_label.configure(text="Current password is incorrect.")
                return
            if len(new) < 6:
                error_label.configure(text="New password must be at least 6 characters.")
                return
            if new != confirm:
                error_label.configure(text="New passwords don't match.")
                return

            change_password(self.user["user_id"], new)
            messagebox.showinfo("Success", "Password updated successfully!")
            current_entry.delete(0, "end")
            new_entry.delete(0, "end")
            confirm_entry.delete(0, "end")
            error_label.configure(text="")

        ctk.CTkButton(frame, text="Update Password", width=300,
                     command=update_password).pack(pady=16)