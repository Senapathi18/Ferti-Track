# main.py — FertiTrack Complete Fixed Version
import customtkinter as ctk
import os
import datetime
from database import (init_db, login_user, get_all_products,
                      get_current_stock, get_sales_report,
                      get_all_customers, get_expiring_batches,
                      get_low_stock_products)
from config import APP_NAME, APP_VERSION

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Safe imports — app still works even if a module has an error
try:
    from modules import products as prod_mod
    PRODUCTS_OK = True
except Exception as e:
    print(f"products import error: {e}")
    PRODUCTS_OK = False

try:
    from modules import inward as inward_mod
    INWARD_OK = True
except Exception as e:
    print(f"inward import error: {e}")
    INWARD_OK = False

try:
    from modules import outward as outward_mod
    OUTWARD_OK = True
except Exception as e:
    print(f"outward import error: {e}")
    OUTWARD_OK = False

try:
    from modules import customers as cust_mod
    CUSTOMERS_OK = True
except Exception as e:
    print(f"customers import error: {e}")
    CUSTOMERS_OK = False

try:
    from modules import settings as settings_mod
    SETTINGS_OK = True
except Exception as e:
    print(f"settings import error: {e}")
    SETTINGS_OK = False

try:
    from modules import analytics as analytics_mod
    ANALYTICS_OK = True
except Exception as e:
    print(f"analytics import error: {e}")
    ANALYTICS_OK = False

try:
    from modules import credit as credit_mod
    CREDIT_OK = True
except Exception as e:
    print(f"credit import error: {e}")
    CREDIT_OK = False

try:
    from modules import chatbot as chatbot_mod
    CHATBOT_OK = True
except Exception as e:
    print(f"chatbot import error: {e}")
    CHATBOT_OK = False

# ── COLORS ──────────────────────────────────────────────────
NAVY      = "#1e3a5f"
BLUE      = "#2563eb"
BLUE_D    = "#1d4ed8"
WHITE     = "#ffffff"
GRAY_50   = "#f8fafc"
GRAY_100  = "#f1f5f9"
GRAY_200  = "#e2e8f0"
GRAY_800  = "#1e293b"
GRAY_900  = "#0f172a"
GREEN     = "#059669"
AMBER     = "#d97706"
RED       = "#dc2626"


def F(size=13, bold=False):
    return ctk.CTkFont(
        family="Segoe UI", size=size,
        weight="bold" if bold else "normal")


def set_icon(window):
    p = os.path.join("assets", "icon.ico")
    if os.path.exists(p):
        try:
            window.iconbitmap(p)
        except Exception:
            pass


def error_screen(parent, name, err):
    ctk.CTkLabel(parent,
                 text=f"Error loading {name}:\n{err}",
                 text_color=RED, font=F(12),
                 wraplength=600).pack(pady=40)


# ══════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("480x580")
        self.resizable(False, False)
        self.configure(fg_color=GRAY_50)
        set_icon(self)
        self._build()

    def _build(self):
        # Blue accent bar on left
        ctk.CTkFrame(self, fg_color=NAVY, width=6).pack(
            side="left", fill="y")

        main = ctk.CTkFrame(self, fg_color=GRAY_50)
        main.pack(fill="both", expand=True, padx=40)

        ctk.CTkLabel(main, text="🌾",
                     font=F(52)).pack(pady=(50, 0))
        ctk.CTkLabel(main, text="FertiTrack",
                     font=F(30, True),
                     text_color=NAVY).pack(pady=(8, 2))
        ctk.CTkLabel(main, text="Fertilizer Shop Management System",
                     font=F(11), text_color="#64748b").pack()

        ctk.CTkFrame(main, height=1,
                     fg_color=GRAY_200).pack(fill="x", pady=28)

        ctk.CTkLabel(main, text="Username",
                     font=F(12, True),
                     text_color="#475569").pack(anchor="w")
        self.u = ctk.CTkEntry(
            main, placeholder_text="Enter username",
            width=380, font=F(13), height=42,
            corner_radius=8, fg_color=WHITE,
            border_color=GRAY_200)
        self.u.pack(pady=(4, 14))

        ctk.CTkLabel(main, text="Password",
                     font=F(12, True),
                     text_color="#475569").pack(anchor="w")
        self.p = ctk.CTkEntry(
            main, placeholder_text="Enter password",
            show="*", width=380, font=F(13), height=42,
            corner_radius=8, fg_color=WHITE,
            border_color=GRAY_200)
        self.p.pack(pady=(4, 4))
        self.p.bind("<Return>", lambda e: self._login())

        self.err = ctk.CTkLabel(
            main, text="", text_color=RED, font=F(12))
        self.err.pack(pady=6)

        ctk.CTkButton(
            main, text="Sign In →", width=380, height=44,
            font=F(14, True), fg_color=BLUE,
            hover_color=BLUE_D, corner_radius=8,
            command=self._login).pack(pady=4)

        ctk.CTkLabel(
            main,
            text=f"v{APP_VERSION}  |  Default: admin / admin123",
            font=F(10), text_color="#94a3b8").pack(pady=(16, 0))

    def _login(self):
        u = self.u.get().strip()
        p = self.p.get().strip()
        if not u or not p:
            self.err.configure(text="Enter username and password.")
            return
        user = login_user(u, p)
        if user:
            self.destroy()
            Dashboard(dict(user))
        else:
            self.err.configure(text="❌ Invalid username or password.")


# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
class Dashboard(ctk.CTk):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.current = "home"
        self.title(f"FertiTrack  —  {user['full_name']}")
        self.geometry("1300x780")
        self.minsize(1100, 680)
        self.configure(fg_color=GRAY_100)
        set_icon(self)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()

        self.content = ctk.CTkFrame(
            self, fg_color=GRAY_100, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")

        self._show_home()
        self.mainloop()

    # ── SIDEBAR ─────────────────────────────────────────────
    def _build_sidebar(self):
        sb = ctk.CTkFrame(
            self, width=230, corner_radius=0, fg_color=NAVY)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)

        # Brand header
        brand = ctk.CTkFrame(sb, fg_color="#162d4a", height=80)
        brand.pack(fill="x")
        brand.pack_propagate(False)
        ctk.CTkLabel(brand, text="🌾 FertiTrack",
                     font=F(18, True),
                     text_color=WHITE).pack(
            side="left", padx=18, pady=24)

        # User chip
        chip = ctk.CTkFrame(sb, fg_color="#162d4a", height=48)
        chip.pack(fill="x", pady=(0, 8))
        chip.pack_propagate(False)
        ctk.CTkLabel(chip,
                     text=f"👤  {self.user['full_name']}",
                     font=F(11), text_color="#93c5fd").pack(
            side="left", padx=18)
        ctk.CTkLabel(chip,
                     text=self.user["role"].upper(),
                     font=F(9, True), text_color="#60a5fa",
                     fg_color="#1e3a5f",
                     corner_radius=4).pack(side="right", padx=12)

        # Divider
        ctk.CTkFrame(sb, height=1,
                     fg_color="#2d5a87").pack(fill="x", padx=12,
                                              pady=(0, 8))

        # Navigation items
        nav = [
            ("Home",          "home",      self._show_home),
            ("Customers",     "customers", self._show_customers),
            ("Inward Stock",  "inward",    self._show_inward),
            ("Outward Stock", "outward",   self._show_outward),
            ("Credit",        "credit",    self._show_credit),
            ("AI Assistant",  "chatbot",   self._show_chatbot),
        ]

        if self.user["role"] == "admin":
             nav.insert(1, ("Products", "products", self._show_products))
             nav.insert(6, ("Analytics", "analytics", self._show_analytics))

        nav.append(("Settings", "settings", self._show_settings))
        for text, key, cmd in nav:
            btn = ctk.CTkButton(
                sb, text=text, anchor="w", height=44,
                fg_color="transparent",
                hover_color="#2d5a87",
                text_color="#cbd5e1",
                font=F(13, True), corner_radius=8,
                command=lambda k=key, c=cmd: self._nav(k, c))
            btn.pack(fill="x", padx=10, pady=2)

        # Bottom buttons
        btm = ctk.CTkFrame(sb, fg_color=NAVY)
        btm.pack(side="bottom", fill="x", padx=12, pady=12)

        ctk.CTkButton(
            btm, text="🔄  Refresh", height=36,
            fg_color=BLUE, hover_color=BLUE_D,
            font=F(12, True), corner_radius=8,
            command=self._refresh).pack(fill="x", pady=(0, 6))

        ctk.CTkButton(
            btm, text="🚪  Logout", height=36,
            fg_color="#7f1d1d", hover_color="#991b1b",
            font=F(12, True), corner_radius=8,
            command=self._logout).pack(fill="x")

    def _nav(self, key, cmd):
        self.current = key
        cmd()

    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _refresh(self):
        m = {
            "home":      self._show_home,
            "products":  self._show_products,
            "customers": self._show_customers,
            "inward":    self._show_inward,
            "outward":   self._show_outward,
            "credit":    self._show_credit,
            "analytics": self._show_analytics,
            "settings":  self._show_settings,
            "chatbot":   self._show_chatbot,
        }
        m.get(self.current, self._show_home)()

    # ── HOME DASHBOARD ───────────────────────────────────────
    def _show_home(self):
        self.current = "home"
        self._clear()

        scroll = ctk.CTkScrollableFrame(
            self.content, fg_color=GRAY_100)
        scroll.pack(fill="both", expand=True)

        # Greeting bar
        greet = ctk.CTkFrame(
            scroll, fg_color=NAVY, height=72, corner_radius=12)
        greet.pack(fill="x", padx=24, pady=(20, 0))
        greet.pack_propagate(False)
        ctk.CTkLabel(greet,
                     text=f"Good day, {self.user['full_name']} 👋",
                     font=F(22, True),
                     text_color=WHITE).pack(
            side="left", padx=24, pady=16)
        ctk.CTkLabel(greet,
                     text=datetime.date.today().strftime("%d %B %Y"),
                     font=F(12), text_color="#93c5fd").pack(
            side="right", padx=24)

        # Section title
        ctk.CTkLabel(scroll, text="Overview",
                     font=F(16, True),
                     text_color=GRAY_800).pack(
            anchor="w", padx=24, pady=(20, 0))

        # Stat cards
        cards = ctk.CTkFrame(scroll, fg_color="transparent")
        cards.pack(fill="x", padx=24, pady=(8, 0))

        all_sales   = get_sales_report()
        all_prods   = get_all_products()
        all_custs   = get_all_customers()
        expiring    = get_expiring_batches(30)
        low_stock   = get_low_stock_products()
        today_str   = datetime.date.today().isoformat()
        today_rev   = sum(
            s["final_amount"] for s in all_sales
            if str(s["sale_date"])[:10] == today_str)

        stat_data = [
            ("Today's Sales",   f"Rs.{today_rev:,.0f}", "💰", BLUE),
            ("Products",        str(len(all_prods)),     "📦", GREEN),
            ("Customers",       str(len(all_custs)),     "👥", AMBER),
            ("Expiring (30d)",  str(len(expiring)),      "⚠️", RED),
            ("Low Stock",       str(len(low_stock)),     "📉", "#7c3aed"),
            ("Total Sales",     str(len(all_sales)),     "🧾", NAVY),
        ]
        for col, (lbl, val, icon, color) in enumerate(stat_data):
            self._stat_card(cards, lbl, val, icon, color, col)

        # Recent sales
        ctk.CTkLabel(scroll, text="Recent Sales",
                     font=F(16, True),
                     text_color=GRAY_800).pack(
            anchor="w", padx=24, pady=(24, 0))

        tbl = ctk.CTkFrame(scroll, fg_color=WHITE, corner_radius=12)
        tbl.pack(fill="x", padx=24, pady=(8, 0))

        # Table header
        hdr = ctk.CTkFrame(tbl, fg_color=NAVY, corner_radius=0)
        hdr.pack(fill="x")
        for i, (h, w) in enumerate(zip(
                ["Sale #", "Customer", "Amount",
                 "Payment", "Status", "Date"],
                [80, 180, 120, 110, 110, 120])):
            ctk.CTkLabel(hdr, text=h, width=w, anchor="w",
                         font=F(11, True),
                         text_color=WHITE).grid(
                row=0, column=i, padx=8, pady=8)

        recent = list(all_sales)[:8]
        if not recent:
            ctk.CTkLabel(tbl,
                         text="No sales yet — use Outward Stock to record first sale",
                         text_color="#94a3b8",
                         font=F(13)).pack(pady=20)
        else:
            for i, s in enumerate(recent):
                s    = dict(s)
                bg   = GRAY_50 if i % 2 else WHITE
                row  = ctk.CTkFrame(tbl, fg_color=bg, corner_radius=0)
                row.pack(fill="x", pady=1)
                sc   = RED if s["payment_status"] == "Credit" else GREEN
                for j, (val, w) in enumerate(zip([
                    f"#{s['sale_id']}",
                    s["customer_name"] or "Walk-in",
                    f"Rs.{s['final_amount']:,.2f}",
                    s["payment_mode"],
                    s["payment_status"],
                    str(s["sale_date"])[:10],
                ], [80, 180, 120, 110, 110, 120])):
                    c = sc if j == 4 else GRAY_800
                    ctk.CTkLabel(row, text=val, width=w, anchor="w",
                                 font=F(12), text_color=c).grid(
                        row=0, column=j, padx=8, pady=7)

        # Alerts
        if expiring:
            ctk.CTkLabel(scroll, text="⚠️ Expiry Alerts",
                         font=F(16, True),
                         text_color=RED).pack(
                anchor="w", padx=24, pady=(20, 0))
            af = ctk.CTkFrame(scroll, fg_color=WHITE,
                              corner_radius=12)
            af.pack(fill="x", padx=24, pady=(8, 0))
            for e in expiring[:5]:
                e = dict(e)
                d = int(e["days_left"])
                c = RED if d <= 10 else (AMBER if d <= 20 else GRAY_800)
                ctk.CTkLabel(af,
                             text=f"⚠️  {e['product_name']}  —  "
                                  f"expires {e['expiry_date']}  "
                                  f"({d} days)",
                             font=F(12), text_color=c).pack(
                    anchor="w", padx=16, pady=8)

        if low_stock:
            ctk.CTkLabel(scroll, text="📉 Low Stock",
                         font=F(16, True),
                         text_color=AMBER).pack(
                anchor="w", padx=24, pady=(16, 0))
            lf = ctk.CTkFrame(scroll, fg_color=WHITE,
                              corner_radius=12)
            lf.pack(fill="x", padx=24, pady=(8, 24))
            for item in low_stock[:5]:
                ctk.CTkLabel(lf,
                             text=f"📉  {item['name']}  —  "
                                  f"{item['stock']} {item['unit']} left  "
                                  f"(min: {item['min']})",
                             font=F(12), text_color=AMBER).pack(
                    anchor="w", padx=16, pady=8)

    def _stat_card(self, parent, label, value, icon, color, col):
        card = ctk.CTkFrame(parent, fg_color=WHITE,
                            corner_radius=12,
                            border_width=2,
                            border_color=GRAY_200)
        card.grid(row=0, column=col, padx=6, pady=6, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        ctk.CTkFrame(card, fg_color=color,
                     height=4, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(card, text=icon,
                     font=F(26)).pack(anchor="w",
                                      padx=14, pady=(10, 0))
        ctk.CTkLabel(card, text=value,
                     font=F(22, True),
                     text_color=GRAY_900).pack(anchor="w",
                                               padx=14, pady=(2, 0))
        ctk.CTkLabel(card, text=label,
                     font=F(11),
                     text_color="#94a3b8").pack(anchor="w",
                                                padx=14,
                                                pady=(2, 12))

    # ── SCREEN METHODS ───────────────────────────────────────
    def _show_products(self):
        self.current = "products"
        self._clear()
        if PRODUCTS_OK:
            prod_mod.ProductsScreen(self.content, self.user)
        else:
            error_screen(self.content, "Products", "Import failed")

    def _show_customers(self):
        self.current = "customers"
        self._clear()
        if CUSTOMERS_OK:
            cust_mod.CustomersScreen(self.content, self.user)
        else:
            error_screen(self.content, "Customers", "Import failed")

    def _show_inward(self):
        self.current = "inward"
        self._clear()
        if INWARD_OK:
            inward_mod.InwardScreen(self.content, self.user)
        else:
            error_screen(self.content, "Inward Stock", "Import failed")

    def _show_outward(self):
        self.current = "outward"
        self._clear()
        if OUTWARD_OK:
            outward_mod.OutwardScreen(self.content, self.user)
        else:
            error_screen(self.content, "Outward Stock", "Import failed")

    def _show_credit(self):
        self.current = "credit"
        self._clear()
        if CREDIT_OK:
            credit_mod.CreditScreen(self.content, self.user)
        else:
            error_screen(self.content, "Credit", "Import failed")

    def _show_analytics(self):
        self.current = "analytics"
        self._clear()
        if ANALYTICS_OK:
            analytics_mod.AnalyticsScreen(self.content, self.user)
        else:
            error_screen(self.content, "Analytics", "Import failed")

    def _show_settings(self):
        self.current = "settings"
        self._clear()
        if SETTINGS_OK:
            settings_mod.SettingsScreen(self.content, self.user)
        else:
            error_screen(self.content, "Settings", "Import failed")

    def _show_chatbot(self):
        self.current = "chatbot"
        self._clear()
        if CHATBOT_OK:
            chatbot_mod.ChatbotScreen(self.content, self.user)
        else:
            # Show helpful message if chatbot module failed
            frame = ctk.CTkFrame(
                self.content, fg_color=WHITE, corner_radius=12)
            frame.pack(fill="both", expand=True,
                       padx=40, pady=40)
            ctk.CTkLabel(frame, text="🤖 FertiBot",
                         font=F(24, True),
                         text_color=NAVY).pack(pady=(40, 8))
            ctk.CTkLabel(frame,
                         text="AI Assistant not loaded.\n\n"
                              "Possible reasons:\n"
                              "1. anthropic library not installed\n"
                              "2. Missing ANTHROPIC_API_KEY in config.py\n"
                              "3. An error in chatbot.py\n\n"
                              "Fix: Run this in terminal:\n"
                              "python -m pip install anthropic",
                         font=F(13), text_color=GRAY_800,
                         justify="left").pack(pady=16, padx=40)

    def _logout(self):
        self.destroy()
        LoginWindow().mainloop()


if __name__ == "__main__":
    init_db()
    LoginWindow().mainloop()