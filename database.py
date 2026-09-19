# database.py — Complete database for FertiTrack

import sqlite3
import hashlib
import os
from config import DB_PATH


# ══════════════════════════════════════════════════════════════
# CONNECTION
# ══════════════════════════════════════════════════════════════

def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ══════════════════════════════════════════════════════════════
# TABLE CREATION
# ══════════════════════════════════════════════════════════════

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name     TEXT NOT NULL,
            role          TEXT NOT NULL CHECK(role IN ('admin','staff')),
            is_active     INTEGER DEFAULT 1,
            created_at    TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            phone       TEXT,
            village     TEXT,
            district    TEXT,
            notes       TEXT,
            created_at  TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name  TEXT NOT NULL UNIQUE,
            category      TEXT NOT NULL,
            unit          TEXT NOT NULL,
            hsn_code      TEXT DEFAULT '',
            gst_rate      REAL DEFAULT 5,
            current_price REAL DEFAULT 0,
            min_stock     REAL DEFAULT 0,
            description   TEXT,
            is_active     INTEGER DEFAULT 1,
            created_at    TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inward_stock (
            inward_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id        INTEGER NOT NULL,
            supplier_name     TEXT NOT NULL,
            quantity_received REAL NOT NULL,
            purchase_price    REAL NOT NULL,
            batch_number      TEXT,
            expiry_date       TEXT,
            invoice_number    TEXT,
            notes             TEXT,
            date_of_entry     TEXT DEFAULT (datetime('now','localtime')),
            created_by        INTEGER,
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (created_by) REFERENCES users(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id    INTEGER,
            total_amount   REAL NOT NULL,
            discount       REAL DEFAULT 0,
            final_amount   REAL NOT NULL,
            payment_mode   TEXT DEFAULT 'Cash',
            payment_status TEXT DEFAULT 'Paid',
            gst_amount     REAL DEFAULT 0,
            notes          TEXT,
            sale_date      TEXT DEFAULT (datetime('now','localtime')),
            created_by     INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (created_by)  REFERENCES users(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outward_stock (
            outward_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id       INTEGER NOT NULL,
            product_id    INTEGER NOT NULL,
            quantity_sold REAL NOT NULL,
            selling_price REAL NOT NULL,
            line_total    REAL NOT NULL,
            gst_rate      REAL DEFAULT 5,
            gst_amount    REAL DEFAULT 0,
            date_of_entry TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (sale_id)    REFERENCES sales(sale_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            log_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER,
            username  TEXT,
            action    TEXT NOT NULL,
            details   TEXT,
            timestamp TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS credit_payments (
            payment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id  INTEGER NOT NULL,
            sale_id      INTEGER,
            amount_paid  REAL NOT NULL,
            payment_mode TEXT DEFAULT 'Cash',
            notes        TEXT,
            paid_date    TEXT DEFAULT (datetime('now','localtime')),
            created_by   INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (sale_id)     REFERENCES sales(sale_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ap_villages (
            village_id INTEGER PRIMARY KEY AUTOINCREMENT,
            district   TEXT NOT NULL,
            mandal     TEXT NOT NULL,
            village    TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_villages_search
        ON ap_villages (district, mandal, village)
    """)

    conn.commit()
    conn.close()
    print("✅ All tables created.")


def migrate_db():
    """Adds new columns to existing tables safely."""
    conn = get_connection()
    cursor = conn.cursor()
    migrations = [
        "ALTER TABLE products ADD COLUMN hsn_code TEXT DEFAULT ''",
        "ALTER TABLE products ADD COLUMN gst_rate REAL DEFAULT 5",
        "ALTER TABLE sales ADD COLUMN gst_amount REAL DEFAULT 0",
        "ALTER TABLE outward_stock ADD COLUMN gst_rate REAL DEFAULT 5",
        "ALTER TABLE outward_stock ADD COLUMN gst_amount REAL DEFAULT 0",
    ]
    for sql in migrations:
        try:
            cursor.execute(sql)
        except Exception:
            pass
    conn.commit()
    conn.close()


def init_db():
    create_tables()
    migrate_db()
    create_default_admin()


# ══════════════════════════════════════════════════════════════
# PASSWORD HELPERS
# ══════════════════════════════════════════════════════════════

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ══════════════════════════════════════════════════════════════
# USER FUNCTIONS
# ══════════════════════════════════════════════════════════════

def create_default_admin():
    conn = get_connection()
    cursor = conn.cursor()
    count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count == 0:
        cursor.execute("""
            INSERT INTO users (username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?)
        """, ("admin", hash_password("admin123"), "Shop Owner", "admin"))
        conn.commit()
        print("✅ Default admin created. Username: admin | Password: admin123")
    conn.close()


def login_user(username: str, password: str):
    conn = get_connection()
    user = conn.execute("""
        SELECT * FROM users
        WHERE username = ? AND password_hash = ? AND is_active = 1
    """, (username, hash_password(password))).fetchone()
    conn.close()
    if user:
        log_action(user["user_id"], user["username"], "LOGIN", "Successful login")
    else:
        log_action(None, username, "LOGIN_FAILED", "Invalid credentials")
    return user


def get_all_users():
    conn = get_connection()
    rows = conn.execute("""
        SELECT user_id, username, full_name, role, is_active, created_at
        FROM users ORDER BY created_at
    """).fetchall()
    conn.close()
    return rows


def create_user(username, password, full_name, role):
    conn = get_connection()
    cursor = conn.cursor()
    existing = cursor.execute(
        "SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        conn.close()
        return False, "Username already exists."
    cursor.execute("""
        INSERT INTO users (username, password_hash, full_name, role)
        VALUES (?, ?, ?, ?)
    """, (username, hash_password(password), full_name, role))
    conn.commit()
    conn.close()
    return True, "User created."


def toggle_user_active(user_id, is_active):
    conn = get_connection()
    conn.execute(
        "UPDATE users SET is_active = ? WHERE user_id = ?",
        (is_active, user_id))
    conn.commit()
    conn.close()


def change_password(user_id, new_password):
    conn = get_connection()
    conn.execute(
        "UPDATE users SET password_hash = ? WHERE user_id = ?",
        (hash_password(new_password), user_id))
    conn.commit()
    conn.close()


def verify_current_password(user_id, password):
    conn = get_connection()
    user = conn.execute("""
        SELECT 1 FROM users WHERE user_id = ? AND password_hash = ?
    """, (user_id, hash_password(password))).fetchone()
    conn.close()
    return user is not None


# ══════════════════════════════════════════════════════════════
# AUDIT LOG
# ══════════════════════════════════════════════════════════════

def log_action(user_id, username, action, details=""):
    conn = get_connection()
    conn.execute("""
        INSERT INTO audit_log (user_id, username, action, details)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, action, details))
    conn.commit()
    conn.close()


def get_audit_log(limit=200):
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return rows


# ══════════════════════════════════════════════════════════════
# CUSTOMER FUNCTIONS
# ══════════════════════════════════════════════════════════════

def add_customer(name, phone="", village="", district="", notes=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customers (name, phone, village, district, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (name, phone, village, district, notes))
    conn.commit()
    customer_id = cursor.lastrowid
    conn.close()
    return customer_id


def get_all_customers():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM customers ORDER BY name").fetchall()
    conn.close()
    return rows


def search_customers(query):
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM customers
        WHERE name LIKE ? OR phone LIKE ?
        ORDER BY name
    """, (f"%{query}%", f"%{query}%")).fetchall()
    conn.close()
    return rows


def get_customer_purchase_history(customer_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT sale_id, sale_date, final_amount, payment_status
        FROM sales WHERE customer_id = ?
        ORDER BY sale_date DESC
    """, (customer_id,)).fetchall()
    conn.close()
    return rows


def delete_customer(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    has_sales = cursor.execute(
        "SELECT COUNT(*) FROM sales WHERE customer_id = ?",
        (customer_id,)).fetchone()[0]
    if has_sales > 0:
        cursor.execute(
            "UPDATE sales SET customer_id = NULL WHERE customer_id = ?",
            (customer_id,))
    cursor.execute(
        "DELETE FROM customers WHERE customer_id = ?", (customer_id,))
    conn.commit()
    conn.close()
    return has_sales


# ══════════════════════════════════════════════════════════════
# CREDIT FUNCTIONS
# ══════════════════════════════════════════════════════════════

def get_customer_outstanding(customer_id):
    conn = get_connection()
    total_credit = conn.execute("""
        SELECT COALESCE(SUM(final_amount), 0) FROM sales
        WHERE customer_id = ? AND payment_status IN ('Credit','Partial')
    """, (customer_id,)).fetchone()[0]
    total_paid = conn.execute("""
        SELECT COALESCE(SUM(amount_paid), 0)
        FROM credit_payments WHERE customer_id = ?
    """, (customer_id,)).fetchone()[0]
    conn.close()
    return round(total_credit - total_paid, 2)


def get_all_credit_customers():
    conn = get_connection()
    customers = conn.execute("""
        SELECT DISTINCT c.customer_id, c.name, c.phone, c.village
        FROM customers c
        JOIN sales s ON c.customer_id = s.customer_id
        WHERE s.payment_status IN ('Credit','Partial')
    """).fetchall()
    conn.close()
    result = []
    for c in customers:
        outstanding = get_customer_outstanding(c["customer_id"])
        if outstanding > 0:
            result.append({**dict(c), "outstanding": outstanding})
    return sorted(result, key=lambda x: x["outstanding"], reverse=True)


def record_credit_payment(customer_id, amount, payment_mode="Cash",
                          sale_id=None, notes="", user_id=None):
    conn = get_connection()
    conn.execute("""
        INSERT INTO credit_payments
            (customer_id, sale_id, amount_paid, payment_mode, notes, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (customer_id, sale_id, amount, payment_mode, notes, user_id))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════════
# PRODUCT FUNCTIONS
# ══════════════════════════════════════════════════════════════

def add_product(name, category, unit, price, min_stock=0,
                description="", hsn_code="", gst_rate=5):
    conn = get_connection()
    conn.execute("""
        INSERT INTO products
            (product_name, category, unit, current_price,
             min_stock, description, hsn_code, gst_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, category, unit, price, min_stock,
          description, hsn_code, gst_rate))
    conn.commit()
    conn.close()


def get_all_products():
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM products WHERE is_active = 1
        ORDER BY product_name
    """).fetchall()
    conn.close()
    return rows


def get_current_stock(product_id):
    conn = get_connection()
    inward = conn.execute("""
        SELECT COALESCE(SUM(quantity_received), 0)
        FROM inward_stock WHERE product_id = ?
    """, (product_id,)).fetchone()[0]
    outward = conn.execute("""
        SELECT COALESCE(SUM(quantity_sold), 0)
        FROM outward_stock WHERE product_id = ?
    """, (product_id,)).fetchone()[0]
    conn.close()
    return inward - outward


def delete_product(product_id):
    conn = get_connection()
    conn.execute(
        "UPDATE products SET is_active = 0 WHERE product_id = ?",
        (product_id,))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════════
# INWARD STOCK FUNCTIONS
# ══════════════════════════════════════════════════════════════

def add_inward_stock(product_id, supplier, qty, price,
                     batch="", expiry="", invoice="",
                     notes="", user_id=None):
    conn = get_connection()
    conn.execute("""
        INSERT INTO inward_stock
            (product_id, supplier_name, quantity_received, purchase_price,
             batch_number, expiry_date, invoice_number, notes, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (product_id, supplier, qty, price,
          batch, expiry, invoice, notes, user_id))
    conn.execute(
        "UPDATE products SET current_price = ? WHERE product_id = ?",
        (price, product_id))
    conn.commit()
    log_action(user_id, "", "STOCK_ADDED",
               f"{qty} units of product #{product_id} from {supplier}")
    conn.close()


def get_inward_history(product_id=None):
    conn = get_connection()
    if product_id:
        rows = conn.execute("""
            SELECT i.*, p.product_name FROM inward_stock i
            JOIN products p ON i.product_id = p.product_id
            WHERE i.product_id = ?
            ORDER BY i.date_of_entry DESC
        """, (product_id,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT i.*, p.product_name FROM inward_stock i
            JOIN products p ON i.product_id = p.product_id
            ORDER BY i.date_of_entry DESC
        """).fetchall()
    conn.close()
    return rows


def delete_inward_entry(inward_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM inward_stock WHERE inward_id = ?", (inward_id,))
    conn.commit()
    conn.close()


def get_expiring_batches(days=60):
    conn = get_connection()
    rows = conn.execute("""
        SELECT i.inward_id, p.product_name, i.batch_number,
               i.expiry_date, i.quantity_received,
               julianday(i.expiry_date) - julianday('now') AS days_left
        FROM inward_stock i
        JOIN products p ON i.product_id = p.product_id
        WHERE i.expiry_date != ''
          AND julianday(i.expiry_date) - julianday('now') <= ?
          AND julianday(i.expiry_date) - julianday('now') >= -9999
        ORDER BY i.expiry_date ASC
    """, (days,)).fetchall()
    conn.close()
    return rows


def get_expiring_soon(days=30):
    return get_expiring_batches(days)


def get_low_stock_products():
    all_prods = get_all_products()
    result = []
    for p in all_prods:
        p = dict(p)
        stock = get_current_stock(p["product_id"])
        if stock <= p["min_stock"]:
            result.append({
                "name":  p["product_name"],
                "stock": stock,
                "min":   p["min_stock"],
                "unit":  p["unit"]
            })
    return result


# ══════════════════════════════════════════════════════════════
# SALES FUNCTIONS
# ══════════════════════════════════════════════════════════════

def add_sale(customer_id, items: list, discount=0,
             payment_mode="Cash", payment_status="Paid",
             notes="", user_id=None):
    total = sum(i["qty"] * i["price"] for i in items)
    final = total - discount
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sales
            (customer_id, total_amount, discount, final_amount,
             payment_mode, payment_status, notes, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (customer_id, total, discount, final,
          payment_mode, payment_status, notes, user_id))
    sale_id = cursor.lastrowid
    for item in items:
        cursor.execute("""
            INSERT INTO outward_stock
                (sale_id, product_id, quantity_sold,
                 selling_price, line_total)
            VALUES (?, ?, ?, ?, ?)
        """, (sale_id, item["product_id"], item["qty"],
              item["price"], item["qty"] * item["price"]))
    conn.commit()
    conn.close()
    log_action(user_id, "", "SALE_CREATED",
               f"Sale #{sale_id}, amount ₹{final:.2f}")
    return sale_id


def get_sales_report(from_date=None, to_date=None):
    conn = get_connection()
    query = """
        SELECT s.sale_id, s.sale_date, s.final_amount,
               s.payment_mode, s.payment_status,
               c.name as customer_name
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.customer_id
    """
    params = []
    if from_date and to_date:
        query += " WHERE date(s.sale_date) BETWEEN ? AND ?"
        params = [from_date, to_date]
    query += " ORDER BY s.sale_date DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_sale_with_items(sale_id):
    conn = get_connection()
    sale = conn.execute("""
        SELECT s.*, c.name as customer_name,
               c.phone as customer_phone,
               c.village as customer_village
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.customer_id
        WHERE s.sale_id = ?
    """, (sale_id,)).fetchone()
    items = conn.execute("""
        SELECT o.*, p.product_name, p.unit
        FROM outward_stock o
        JOIN products p ON o.product_id = p.product_id
        WHERE o.sale_id = ?
    """, (sale_id,)).fetchall()
    conn.close()
    return sale, items


def delete_sale(sale_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM outward_stock WHERE sale_id = ?", (sale_id,))
    conn.execute(
        "DELETE FROM sales WHERE sale_id = ?", (sale_id,))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════════
# GST FUNCTIONS
# ══════════════════════════════════════════════════════════════

def get_gst_rate_for_product(product_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT gst_rate FROM products WHERE product_id = ?",
        (product_id,)).fetchone()
    conn.close()
    return row["gst_rate"] if row else 5


def get_gst_summary_for_invoice(sale_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT o.line_total, o.gst_rate, p.hsn_code, p.product_name
        FROM outward_stock o
        JOIN products p ON o.product_id = p.product_id
        WHERE o.sale_id = ?
    """, (sale_id,)).fetchall()
    conn.close()
    gst_summary = {}
    for row in rows:
        rate = row["gst_rate"] or 5
        taxable = row["line_total"] / (1 + rate / 100)
        gst_amount = row["line_total"] - taxable
        if rate not in gst_summary:
            gst_summary[rate] = {
                "taxable": 0, "cgst": 0,
                "sgst": 0, "hsn": row["hsn_code"]}
        gst_summary[rate]["taxable"] += taxable
        gst_summary[rate]["cgst"]    += gst_amount / 2
        gst_summary[rate]["sgst"]    += gst_amount / 2
    return gst_summary


# ══════════════════════════════════════════════════════════════
# ANALYTICS FUNCTIONS
# ══════════════════════════════════════════════════════════════

def get_monthly_sales():
    conn = get_connection()
    rows = conn.execute("""
        SELECT strftime('%Y-%m', sale_date) AS month,
               SUM(final_amount) AS total
        FROM sales GROUP BY month ORDER BY month
    """).fetchall()
    conn.close()
    return rows


def get_profit_loss_data():
    conn = get_connection()
    rows = conn.execute("""
        SELECT strftime('%Y-%m', s.sale_date) AS month,
               SUM(o.line_total) AS revenue,
               SUM(o.quantity_sold * (
                   SELECT AVG(purchase_price)
                   FROM inward_stock
                   WHERE product_id = o.product_id
               )) AS cost
        FROM outward_stock o
        JOIN sales s ON o.sale_id = s.sale_id
        GROUP BY month ORDER BY month
    """).fetchall()
    conn.close()
    return rows


def get_customer_buying_patterns():
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.name, c.village,
               COUNT(s.sale_id)      AS num_purchases,
               SUM(s.final_amount)   AS total_spent,
               AVG(s.final_amount)   AS avg_order_value,
               MAX(s.sale_date)      AS last_purchase
        FROM customers c
        JOIN sales s ON c.customer_id = s.customer_id
        GROUP BY c.customer_id
        ORDER BY total_spent DESC
    """).fetchall()
    conn.close()
    return rows


def get_top_products():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.product_name,
               SUM(o.quantity_sold) AS total_qty,
               SUM(o.line_total)    AS total_revenue
        FROM outward_stock o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY p.product_id
        ORDER BY total_revenue DESC
        LIMIT 10
    """).fetchall()
    conn.close()
    return rows


# ══════════════════════════════════════════════════════════════
# VILLAGE / LOCATION FUNCTIONS
# ══════════════════════════════════════════════════════════════

def get_all_districts():
    conn = get_connection()
    rows = conn.execute("""
        SELECT DISTINCT district FROM ap_villages ORDER BY district
    """).fetchall()
    conn.close()
    return [r["district"] for r in rows]


def get_mandals_for_district(district):
    conn = get_connection()
    rows = conn.execute("""
        SELECT DISTINCT mandal FROM ap_villages
        WHERE district = ? ORDER BY mandal
    """, (district,)).fetchall()
    conn.close()
    return [r["mandal"] for r in rows]


def get_villages_for_mandal(district, mandal):
    conn = get_connection()
    rows = conn.execute("""
        SELECT village FROM ap_villages
        WHERE district = ? AND mandal = ?
        ORDER BY village
    """, (district, mandal)).fetchall()
    conn.close()
    return [r["village"] for r in rows]


def search_villages_db(district, mandal, query):
    conn = get_connection()
    rows = conn.execute("""
        SELECT village FROM ap_villages
        WHERE district = ? AND mandal = ?
        AND village LIKE ? ORDER BY village LIMIT 15
    """, (district, mandal, f"%{query}%")).fetchall()
    conn.close()
    return [r["village"] for r in rows]


def is_villages_populated():
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM ap_villages").fetchone()[0]
    conn.close()
    return count > 0


def add_village(district, mandal, village):
    conn = get_connection()
    existing = conn.execute("""
        SELECT 1 FROM ap_villages
        WHERE district=? AND mandal=? AND village=?
    """, (district, mandal, village)).fetchone()
    if not existing:
        conn.execute("""
            INSERT INTO ap_villages (district, mandal, village)
            VALUES (?, ?, ?)
        """, (district, mandal, village))
        conn.commit()
    conn.close()