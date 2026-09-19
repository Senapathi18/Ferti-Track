# modules/chatbot.py
# FertiTrack AI Assistant — Powered by Google Gemini
# Supports: Shop data, General questions, Multi-language

import customtkinter as ctk
from tkinter import messagebox
import threading
import datetime

from database import (
    get_sales_report, get_all_products, get_current_stock,
    get_all_customers, get_customer_outstanding,
    get_monthly_sales, get_top_products,
    get_expiring_batches, get_low_stock_products
)

# ── COLORS & FONTS ───────────────────────────────────────────
NAVY  = "#1e3a5f"
BLUE  = "#2563eb"
BLUE2 = "#1d4ed8"
WHITE = "#ffffff"
G50   = "#f8fafc"
G100  = "#f1f5f9"
G200  = "#e2e8f0"
G400  = "#94a3b8"
G800  = "#1e293b"
G900  = "#0f172a"
GREEN = "#059669"
AMBER = "#d97706"
RED   = "#dc2626"


def F(size=13, bold=False):
    return ctk.CTkFont(
        family="Segoe UI", size=size,
        weight="bold" if bold else "normal")


# ── LANGUAGE SETTINGS ────────────────────────────────────────
LANGUAGES = {
    "English":   "en",
    "Telugu":    "te",
    "Hindi":     "hi",
    "Kannada":   "kn",
    "Tamil":     "ta",
}

LANG_INSTRUCTIONS = {
    "en": "Always respond in English.",
    "te": "Always respond in Telugu language using Telugu script.",
    "hi": "Always respond in Hindi language using Devanagari script.",
    "kn": "Always respond in Kannada language using Kannada script.",
    "ta": "Always respond in Tamil language using Tamil script.",
}

# ── QUICK ACTION CATEGORIES ──────────────────────────────────
QUICK_ACTIONS = {
    "📊 Shop Data": [
        "What are today's total sales?",
        "Who owes me the most money?",
        "What is my best selling product?",
        "Which stock is expiring soon?",
        "What are my low stock items?",
        "Show monthly revenue summary",
        "How many customers do I have?",
        "What is my total revenue ever?",
    ],
    "🛠️ How To": [
        "How do I add a new product?",
        "How do I record a sale?",
        "How do I add a customer?",
        "How do I record inward stock?",
        "How do I generate a PDF invoice?",
        "How do I create a staff account?",
        "How do I change my password?",
        "How do I delete a record?",
    ],
    "⚙️ Settings": [
        "Where is password change option?",
        "How do I find the audit log?",
        "How do I manage user accounts?",
        "How do I set minimum stock alerts?",
        "Where are my invoices saved?",
        "How do I back up my database?",
        "What does the refresh button do?",
        "How do I disable a staff account?",
    ],
    "💡 General": [
        "What is the weather like today?",
        "What is the price of Urea today?",
        "Tell me a farming tip for AP",
        "What are the fertilizer subsidy rules?",
        "Explain GST for fertilizers",
        "What is DAP fertilizer used for?",
        "Best crops for Kharif season in AP?",
        "How to store fertilizers safely?",
    ],
}

SYSTEM_BASE = """You are FertiBot, the AI assistant inside FertiTrack 
fertilizer shop management software in Andhra Pradesh, India.

You are like a full Gemini AI — you can answer ANY question the user 
asks, not just shop-related ones. You are helpful, friendly, and 
knowledgeable about everything.

When the user asks about their shop data, use the data provided.
When the user asks general questions, answer from your knowledge.
When the user asks how to use FertiTrack software, give clear steps.

=== FERTITRACK SOFTWARE GUIDE ===
Navigation:
- Home: dashboard with sales stats and alerts
- Products: add/delete products with HSN and GST
- Customers: add/delete customers with AP location
- Inward Stock: record stock received from suppliers
- Outward Stock: record sales, multi-item cart, PDF invoice
- Credit: track farmers who owe money
- Analytics: charts, forecast, P&L
- Settings: password, staff accounts, audit log
- AI Assistant: this screen

Common tasks:
- Add product: Products > + Add Product > fill form > Save
- Record sale: Outward Stock > + New Sale > add items > Complete Sale
- Add customer: Customers > + Add Customer > fill details > Save
- Check credit: Click Credit in sidebar
- Change password: Settings > Change Password tab
- Create staff: Settings > Staff Accounts > + Add Staff (admin only)
- Delete anything: click red Delete button in any table row
- Refresh: click Refresh button at bottom of sidebar

GST rates:
- Urea, DAP, NPK, MOP, SSP: 5% GST
- Pesticides, Herbicides: 18% GST
- Seeds: 0% GST exempt

Rules:
- Use Rs. for currency
- Be concise but complete
- For shop questions use the data provided
- For general questions use your full knowledge
- Always be helpful and friendly
"""


def get_shop_context():
    """Gets current shop data snapshot for AI context."""
    today = datetime.date.today().isoformat()
    lines = [f"Today: {today}\n"]

    try:
        sales   = get_sales_report()
        rev     = sum(s["final_amount"] for s in sales)
        t_sales = [s for s in sales
                   if str(s["sale_date"])[:10] == today]
        t_rev   = sum(s["final_amount"] for s in t_sales)

        lines.append(f"SALES: total={len(sales)}, "
                     f"revenue=Rs.{rev:,.0f}, "
                     f"today=Rs.{t_rev:,.0f}")
        for s in list(sales)[:5]:
            s = dict(s)
            lines.append(
                f"  #{s['sale_id']} | "
                f"{s['customer_name'] or 'Walk-in'} | "
                f"Rs.{s['final_amount']:.0f} | "
                f"{s['payment_status']}")

        prods = get_all_products()
        lines.append(f"\nPRODUCTS ({len(prods)}):")
        for p in prods:
            p  = dict(p)
            st = get_current_stock(p["product_id"])
            lines.append(
                f"  {p['product_name']}: "
                f"{st} {p['unit']} @ Rs.{p['current_price']:.0f}")

        custs = get_all_customers()
        lines.append(f"\nCUSTOMERS ({len(custs)}):")
        for c in custs:
            c   = dict(c)
            owe = get_customer_outstanding(c["customer_id"])
            lines.append(
                f"  {c['name']} | {c['phone'] or '-'} | "
                f"owes Rs.{owe:.0f}")

        low = get_low_stock_products()
        if low:
            lines.append(f"\nLOW STOCK ({len(low)}):")
            for x in low:
                lines.append(
                    f"  {x['name']}: {x['stock']} {x['unit']}")

        exp = get_expiring_batches(60)
        if exp:
            lines.append(f"\nEXPIRING ({len(exp)}):")
            for e in exp:
                e = dict(e)
                lines.append(
                    f"  {e['product_name']}: "
                    f"{e['expiry_date']} "
                    f"({int(e['days_left'])}d)")

        top = get_top_products()
        if top:
            lines.append("\nTOP PRODUCTS:")
            for p in top:
                p = dict(p)
                lines.append(
                    f"  {p['product_name']}: "
                    f"Rs.{p['total_revenue']:,.0f}")

        monthly = get_monthly_sales()
        if monthly:
            lines.append("\nMONTHLY SALES:")
            for m in monthly:
                m = dict(m)
                lines.append(
                    f"  {m['month']}: Rs.{m['total']:,.0f}")

    except Exception as e:
        lines.append(f"(Some data unavailable: {e})")

    return "\n".join(lines)


def check_gemini():
    """Returns True if Gemini is configured and ready."""
    try:
        from modules.llm import is_llm_ready
        return is_llm_ready()
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════
# CHATBOT SCREEN
# ══════════════════════════════════════════════════════════════

class ChatbotScreen(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color=G100)
        self.pack(fill="both", expand=True)
        self.user        = user
        self.history     = []
        self.current_cat = list(QUICK_ACTIONS.keys())[0]
        self.language    = "en"   # default English
        self._build()

    def _build(self):
        # ── HEADER ──────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color=NAVY, height=64)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkLabel(
            hdr, text="🤖  FertiBot — AI Assistant",
            font=F(18, True), text_color=WHITE
        ).pack(side="left", padx=20, pady=16)

        # Gemini status badge
        ready  = check_gemini()
        badge  = "🟢 Gemini Ready" if ready else "🔴 Setup Gemini"
        bcolor = "#6ee7b7" if ready else "#fca5a5"
        ctk.CTkLabel(
            hdr, text=badge,
            font=F(11, True), text_color=bcolor
        ).pack(side="right", padx=16)

        # ── LANGUAGE SELECTOR BAR ────────────────────
        lang_bar = ctk.CTkFrame(self, fg_color=WHITE, height=44)
        lang_bar.pack(fill="x")
        lang_bar.pack_propagate(False)

        ctk.CTkLabel(
            lang_bar, text="Language:",
            font=F(12, True), text_color=G800
        ).pack(side="left", padx=(16, 8), pady=10)

        self.lang_btns = {}
        for lang in LANGUAGES:
            btn = ctk.CTkButton(
                lang_bar, text=lang,
                font=F(11),
                fg_color=BLUE if lang == "English" else G200,
                hover_color=BLUE2,
                text_color=WHITE if lang == "English" else G800,
                height=28, width=80, corner_radius=14,
                command=lambda l=lang: self._set_language(l))
            btn.pack(side="left", padx=3, pady=8)
            self.lang_btns[lang] = btn

        # ── BODY (left panel + chat) ─────────────────
        body = ctk.CTkFrame(self, fg_color=G100)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # ── LEFT PANEL — Quick Actions ───────────────
        left = ctk.CTkFrame(
            body, fg_color=WHITE, width=230,
            border_width=1, border_color=G200)
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_propagate(False)

        ctk.CTkLabel(
            left, text="Quick Actions",
            font=F(13, True), text_color=G900
        ).pack(anchor="w", padx=14, pady=(14, 6))

        # Category tabs
        self.cat_btns = {}
        for cat in QUICK_ACTIONS:
            b = ctk.CTkButton(
                left, text=cat, font=F(11),
                fg_color=BLUE if cat == self.current_cat else G50,
                hover_color="#dbeafe",
                text_color=WHITE if cat == self.current_cat else G800,
                height=30, corner_radius=6, anchor="w",
                command=lambda c=cat: self._set_cat(c))
            b.pack(fill="x", padx=8, pady=2)
            self.cat_btns[cat] = b

        ctk.CTkFrame(
            left, height=1, fg_color=G200
        ).pack(fill="x", padx=8, pady=6)

        # Question list
        self.q_list = ctk.CTkScrollableFrame(
            left, fg_color=WHITE)
        self.q_list.pack(
            fill="both", expand=True, padx=8, pady=(0, 8))
        self._render_questions()

        # ── RIGHT PANEL — Chat ───────────────────────
        right = ctk.CTkFrame(body, fg_color=G100)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # Chat area
        self.chat = ctk.CTkScrollableFrame(right, fg_color=G100)
        self.chat.grid(
            row=0, column=0, sticky="nsew", padx=8, pady=8)

        # Input bar
        inp = ctk.CTkFrame(
            right, fg_color=WHITE, height=68,
            border_width=1, border_color=G200)
        inp.grid(row=1, column=0, sticky="ew")
        inp.grid_columnconfigure(0, weight=1)
        inp.grid_propagate(False)

        self.entry = ctk.CTkEntry(
            inp,
            placeholder_text=(
                "Ask anything — shop data, general questions, "
                "farming tips, software help..."),
            font=F(13), height=44, corner_radius=22,
            border_color=G200, fg_color=G50)
        self.entry.grid(
            row=0, column=0,
            padx=(16, 8), pady=12, sticky="ew")
        self.entry.bind("<Return>", lambda e: self._on_send())

        bframe = ctk.CTkFrame(inp, fg_color="transparent")
        bframe.grid(row=0, column=1, padx=(0, 12), pady=12)

        self.send_btn = ctk.CTkButton(
            bframe, text="Send ➤",
            font=F(12, True),
            fg_color=BLUE, hover_color=BLUE2,
            height=44, width=90, corner_radius=22,
            command=self._on_send)
        self.send_btn.pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            bframe, text="🗑️",
            font=F(14),
            fg_color="#fee2e2", hover_color=RED,
            text_color=RED, height=44, width=44,
            corner_radius=22,
            command=self._clear
        ).pack(side="left")

        # ── WELCOME MESSAGE ──────────────────────────
        self._bot_msg(
            f"👋 Hello {self.user['full_name']}! I'm FertiBot.\n\n"
            "I can help you with ANYTHING:\n"
            "📊 Your shop data — sales, stock, customers, credit\n"
            "🛠️ How to use FertiTrack — step by step\n"
            "⚙️ Find any setting in the software\n"
            "💡 General questions — farming, GST, weather, anything!\n\n"
            "Select a language above, pick a quick action on the left,\n"
            "or just type any question below!")

        if not check_gemini():
            self._bot_msg(
                "⚠️ Gemini AI not set up yet.\n\n"
                "To activate:\n"
                "1. Run: python -m pip install google-generativeai\n"
                "2. Get FREE key: https://aistudio.google.com/app/apikey\n"
                "3. Open config.py and add:\n"
                "   GEMINI_API_KEY = 'AIzaSy...'\n"
                "4. Restart FertiTrack",
                color="#fff7ed")

    # ── LANGUAGE SELECTION ───────────────────────────────────

    def _set_language(self, lang):
        self.language = LANGUAGES[lang]
        for name, btn in self.lang_btns.items():
            if name == lang:
                btn.configure(fg_color=BLUE, text_color=WHITE)
            else:
                btn.configure(fg_color=G200, text_color=G800)

        self._bot_msg(
            f"Language set to {lang}. "
            f"I will now reply in {lang}.")

    # ── CATEGORY SELECTION ───────────────────────────────────

    def _set_cat(self, cat):
        self.current_cat = cat
        for name, btn in self.cat_btns.items():
            if name == cat:
                btn.configure(fg_color=BLUE, text_color=WHITE)
            else:
                btn.configure(fg_color=G50, text_color=G800)
        self._render_questions()

    def _render_questions(self):
        for w in self.q_list.winfo_children():
            w.destroy()
        for q in QUICK_ACTIONS[self.current_cat]:
            ctk.CTkButton(
                self.q_list, text=q,
                font=F(11),
                fg_color=G50, hover_color="#dbeafe",
                text_color="#334155", height=34,
                corner_radius=6, anchor="w",
                border_width=1, border_color=G200,
                command=lambda qu=q: self._send(qu)
            ).pack(fill="x", pady=2)

    # ── CHAT BUBBLES ─────────────────────────────────────────

    def _bot_msg(self, text, color=WHITE):
        row = ctk.CTkFrame(self.chat, fg_color="transparent")
        row.pack(anchor="w", pady=4, fill="x")
        ctk.CTkLabel(
            row, text="🤖", font=F(18)
        ).pack(side="left", anchor="n", padx=(4, 6), pady=6)
        bub = ctk.CTkFrame(
            row, fg_color=color, corner_radius=16,
            border_width=1, border_color=G200)
        bub.pack(side="left", anchor="w", padx=(0, 60))
        ctk.CTkLabel(
            bub, text=text, font=F(13),
            text_color=G800,
            wraplength=500, justify="left"
        ).pack(padx=14, pady=10)
        self._scroll()

    def _user_msg(self, text):
        bub = ctk.CTkFrame(
            self.chat, fg_color=BLUE, corner_radius=16)
        bub.pack(anchor="e", pady=4, padx=(80, 4))
        ctk.CTkLabel(
            bub, text=text, font=F(13),
            text_color=WHITE,
            wraplength=440, justify="left"
        ).pack(padx=14, pady=10)
        self._scroll()

    def _typing_indicator(self):
        row = ctk.CTkFrame(self.chat, fg_color="transparent")
        row.pack(anchor="w", pady=4)
        ctk.CTkLabel(
            row, text="🤖", font=F(18)
        ).pack(side="left", anchor="n", padx=(4, 6), pady=6)
        bub = ctk.CTkFrame(
            row, fg_color=WHITE, corner_radius=16,
            border_width=1, border_color=G200)
        bub.pack(side="left")
        ctk.CTkLabel(
            bub, text="⏳  Thinking...",
            font=F(13), text_color=G400
        ).pack(padx=14, pady=10)
        self._scroll()
        return row

    def _scroll(self):
        self.chat.after(
            100,
            lambda: self.chat._parent_canvas.yview_moveto(1.0))

    # ── SENDING MESSAGES ─────────────────────────────────────

    def _on_send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self._send(text)

    def _send(self, text):
        if not check_gemini():
            messagebox.showwarning(
                "Gemini Not Configured",
                "To use FertiBot:\n\n"
                "1. pip install google-generativeai\n"
                "2. Get key: https://aistudio.google.com/app/apikey\n"
                "3. Add to config.py: GEMINI_API_KEY = 'AIzaSy...'\n"
                "4. Restart the app")
            return

        self._user_msg(text)
        self.send_btn.configure(state="disabled", text="...")
        typing = self._typing_indicator()
        self.history.append({"role": "user", "content": text})
        threading.Thread(
            target=self._call,
            args=(typing, text),
            daemon=True).start()

    def _call(self, typing, question):
        """Calls Gemini in background thread."""
        try:
            from modules.llm import FertiLLM

            # Build system prompt with language instruction
            lang_instr = LANG_INSTRUCTIONS.get(self.language, "")
            system     = SYSTEM_BASE + f"\n\nLANGUAGE RULE: {lang_instr}"

            llm = FertiLLM(system_prompt=system)

            # Restore conversation history
            llm.history = list(self.history[:-1])

            # Get fresh shop data for context
            context = get_shop_context()

            # Ask Gemini
            reply = llm.ask(question, context=context)

            # Save reply to history
            self.history.append({
                "role": "assistant", "content": reply})

            # Show reply on screen
            self.after(0, lambda: self._finish(typing, reply))

        except Exception as e:
            err = f"Error: {str(e)}"
            self.after(0, lambda: self._finish(typing, err))

    def _finish(self, typing_row, reply):
        """Removes typing indicator and shows actual reply."""
        typing_row.destroy()

        # Highlight urgent messages
        color = WHITE
        upper = reply.upper()
        if any(w in upper for w in
               ["EXPIRE", "LOW STOCK", "URGENT", "WARNING"]):
            color = "#fff7ed"
        elif any(w in upper for w in
                 ["ERROR", "FAILED", "INVALID"]):
            color = "#fee2e2"

        self._bot_msg(reply, color=color)
        self.send_btn.configure(state="normal", text="Send ➤")

    # ── CLEAR CHAT ───────────────────────────────────────────

    def _clear(self):
        self.history = []
        for w in self.chat.winfo_children():
            w.destroy()
        self._bot_msg(
            "Chat cleared! Ask me anything — "
            "shop questions, general knowledge, farming tips, "
            "software help... I can answer everything! 🌾")