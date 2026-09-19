# modules/analytics.py — Sales forecast, expiry alerts, P&L, customer patterns

import customtkinter as ctk
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import (get_monthly_sales, get_profit_loss_data, get_expiring_batches,
                      get_low_stock_products, get_customer_buying_patterns, get_top_products)


class AnalyticsScreen(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color="white")
        self.pack(fill="both", expand=True)
        self.user = user

        ctk.CTkLabel(self, text="📊 Analytics",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=20, pady=(20, 10))

        tabs = ctk.CTkTabview(self, width=1000, height=560)
        tabs.pack(fill="both", expand=True, padx=20, pady=10)

        tabs.add("Sales Forecast")
        tabs.add("Expiry Alerts")
        tabs.add("Profit & Loss")
        tabs.add("Customer Patterns")

        self.build_forecast_tab(tabs.tab("Sales Forecast"))
        self.build_expiry_tab(tabs.tab("Expiry Alerts"))
        self.build_pl_tab(tabs.tab("Profit & Loss"))
        self.build_customer_tab(tabs.tab("Customer Patterns"))

    # ──────────────────────────────────────────
    # TAB 1 — SALES FORECAST
    # ──────────────────────────────────────────
    def build_forecast_tab(self, tab):
        data = get_monthly_sales()
        if not data or len(data) < 2:
            ctk.CTkLabel(tab, text="Not enough sales data yet. Record a few sales across "
                              "different months to see trends.",
                        text_color="gray").pack(pady=60)
            return

        df = pd.DataFrame(data, columns=["month", "total"])
        df["total"] = df["total"].astype(float)

        # Simple linear forecast for next month using numpy polyfit
        x = np.arange(len(df))
        y = df["total"].values
        coeffs = np.polyfit(x, y, 1)            # slope & intercept
        next_month_forecast = np.polyval(coeffs, len(df))
        next_month_forecast = max(0, next_month_forecast)  # never negative

        growth_pct = ((y[-1] - y[0]) / y[0] * 100) if y[0] != 0 else 0

        # Metric cards
        metrics_frame = ctk.CTkFrame(tab, fg_color="white")
        metrics_frame.pack(fill="x", pady=(10, 0))
        self.metric_card(metrics_frame, "Next Month Forecast", f"₹{next_month_forecast:,.0f}", 0)
        self.metric_card(metrics_frame, "Overall Growth", f"{growth_pct:+.1f}%", 1)
        self.metric_card(metrics_frame, "Best Month", df.loc[df['total'].idxmax(), 'month'], 2)

        # Chart
        fig = Figure(figsize=(8, 3.5), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(df["month"], df["total"], marker="o", color="#0f6e56", label="Actual")
        forecast_x = list(df["month"]) + ["Next month"]
        forecast_y = list(df["total"]) + [next_month_forecast]
        ax.plot(forecast_x[-2:], forecast_y[-2:], linestyle="--",
               marker="o", color="#d97706", label="Forecast")
        ax.set_title("Monthly Sales Trend")
        ax.set_ylabel("Sales (₹)")
        ax.legend()
        fig.autofmt_xdate(rotation=45)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

    # ──────────────────────────────────────────
    # TAB 2 — EXPIRY ALERTS
    # ──────────────────────────────────────────
    def build_expiry_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="white")
        scroll.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(scroll, text="⚠️ Expiring within 60 days",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(0, 8))

        expiring = get_expiring_batches(days=60)
        if not expiring:
            ctk.CTkLabel(scroll, text="✅ Nothing expiring soon. Great job!",
                        text_color="green").pack(pady=10)
        else:
            headers = ["Product", "Batch", "Expiry Date", "Days Left", "Est. Remaining"]
            header_row = ctk.CTkFrame(scroll, fg_color="#f0f4f8")
            header_row.pack(fill="x", pady=(0, 4))
            for i, h in enumerate(headers):
                ctk.CTkLabel(header_row, text=h, font=ctk.CTkFont(weight="bold"),
                            width=150, anchor="w").grid(row=0, column=i, padx=8, pady=8)

            for e in expiring:
                days_left = int(e["days_left"])
                color = "red" if days_left <= 15 else ("orange" if days_left <= 30 else "black")
                row = ctk.CTkFrame(scroll, fg_color="white", border_width=1, border_color="#eee")
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=e["product_name"], width=150, anchor="w").grid(
                    row=0, column=0, padx=8, pady=8)
                ctk.CTkLabel(row, text=e["batch_number"] or "-", width=150, anchor="w").grid(
                    row=0, column=1, padx=8, pady=8)
                ctk.CTkLabel(row, text=e["expiry_date"], width=150, anchor="w").grid(
                    row=0, column=2, padx=8, pady=8)
                ctk.CTkLabel(row, text=f"{days_left} days", width=150, anchor="w",
                           text_color=color).grid(row=0, column=3, padx=8, pady=8)
                ctk.CTkLabel(row, text=f"{e['remaining_estimate']:.0f}", width=150, anchor="w").grid(
                    row=0, column=4, padx=8, pady=8)

        ctk.CTkLabel(scroll, text="📉 Low Stock Items",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(20, 8))

        low_stock = get_low_stock_products()
        if not low_stock:
            ctk.CTkLabel(scroll, text="✅ All products are sufficiently stocked.",
                        text_color="green").pack(pady=10)
        else:
            for item in low_stock:
                ctk.CTkLabel(scroll,
                           text=f"⚠️ {item['name']}: only {item['stock']} {item['unit']} left "
                                f"(minimum: {item['min']} {item['unit']})",
                           text_color="red", anchor="w").pack(fill="x", pady=3)

    # ──────────────────────────────────────────
    # TAB 3 — PROFIT & LOSS
    # ──────────────────────────────────────────
    def build_pl_tab(self, tab):
        data = get_profit_loss_data()
        if not data:
            ctk.CTkLabel(tab, text="No sales data yet to calculate profit/loss.",
                        text_color="gray").pack(pady=60)
            return

        df = pd.DataFrame(data, columns=["month", "revenue", "cost"])
        df["revenue"] = df["revenue"].fillna(0).astype(float)
        df["cost"] = df["cost"].fillna(0).astype(float)
        df["profit"] = df["revenue"] - df["cost"]

        total_revenue = df["revenue"].sum()
        total_cost = df["cost"].sum()
        total_profit = df["profit"].sum()
        margin = (total_profit / total_revenue * 100) if total_revenue else 0

        metrics_frame = ctk.CTkFrame(tab, fg_color="white")
        metrics_frame.pack(fill="x", pady=(10, 0))
        self.metric_card(metrics_frame, "Total Revenue", f"₹{total_revenue:,.0f}", 0)
        self.metric_card(metrics_frame, "Total Profit", f"₹{total_profit:,.0f}", 1)
        self.metric_card(metrics_frame, "Profit Margin", f"{margin:.1f}%", 2)

        fig = Figure(figsize=(8, 3.5), dpi=100)
        ax = fig.add_subplot(111)
        width = 0.35
        x = np.arange(len(df))
        ax.bar(x - width/2, df["revenue"], width, label="Revenue", color="#0f6e56")
        ax.bar(x + width/2, df["cost"], width, label="Cost", color="#d85a30")
        ax.set_xticks(x)
        ax.set_xticklabels(df["month"], rotation=45)
        ax.set_ylabel("₹")
        ax.set_title("Revenue vs Cost by Month")
        ax.legend()
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

    # ──────────────────────────────────────────
    # TAB 4 — CUSTOMER BUYING PATTERNS
    # ──────────────────────────────────────────
    def build_customer_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="white")
        scroll.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(scroll, text="🏆 Top Customers",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(0, 8))

        customers = get_customer_buying_patterns()
        if not customers:
            ctk.CTkLabel(scroll, text="No customer purchase data yet.",
                        text_color="gray").pack(pady=10)
        else:
            headers = ["Customer", "Village", "Orders", "Total Spent", "Avg Order", "Last Purchase"]
            header_row = ctk.CTkFrame(scroll, fg_color="#f0f4f8")
            header_row.pack(fill="x", pady=(0, 4))
            for i, h in enumerate(headers):
                ctk.CTkLabel(header_row, text=h, font=ctk.CTkFont(weight="bold"),
                            width=130, anchor="w").grid(row=0, column=i, padx=6, pady=8)

            for c in customers[:15]:
                row = ctk.CTkFrame(scroll, fg_color="white", border_width=1, border_color="#eee")
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=c["name"], width=130, anchor="w").grid(
                    row=0, column=0, padx=6, pady=6)
                ctk.CTkLabel(row, text=c["village"] or "-", width=130, anchor="w").grid(
                    row=0, column=1, padx=6, pady=6)
                ctk.CTkLabel(row, text=str(c["num_purchases"]), width=130, anchor="w").grid(
                    row=0, column=2, padx=6, pady=6)
                ctk.CTkLabel(row, text=f"₹{c['total_spent']:,.0f}", width=130, anchor="w").grid(
                    row=0, column=3, padx=6, pady=6)
                ctk.CTkLabel(row, text=f"₹{c['avg_order_value']:,.0f}", width=130, anchor="w").grid(
                    row=0, column=4, padx=6, pady=6)
                ctk.CTkLabel(row, text=str(c["last_purchase"])[:10], width=130, anchor="w").grid(
                    row=0, column=5, padx=6, pady=6)

        ctk.CTkLabel(scroll, text="🔥 Best Selling Products",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(20, 8))

        top_products = get_top_products()
        if top_products:
            df = pd.DataFrame(top_products, columns=["product", "qty", "revenue"])
            fig = Figure(figsize=(8, 3), dpi=100)
            ax = fig.add_subplot(111)
            ax.barh(df["product"], df["revenue"], color="#534ab7")
            ax.set_xlabel("Revenue (₹)")
            ax.invert_yaxis()
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=scroll)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

    # ──────────────────────────────────────────
    # HELPER — metric card widget
    # ──────────────────────────────────────────
    def metric_card(self, parent, label, value, column):
        card = ctk.CTkFrame(parent, fg_color="#f7f7f7", corner_radius=8)
        card.grid(row=0, column=column, padx=8, pady=4, sticky="ew")
        parent.grid_columnconfigure(column, weight=1)
        ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=11), text_color="gray").pack(
            anchor="w", padx=14, pady=(10, 0))
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=18, weight="bold")).pack(
            anchor="w", padx=14, pady=(0, 10))