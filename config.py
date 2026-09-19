# config.py — App-wide settings
# AI Chatbot
GEMINI_API_KEY = "AQ.Ab8RN6IXC1Psw0NALHzpoMfy-liT1ZI_6EX9EzUtO7pJF5B5sA"
APP_NAME    = "FertiTrack"
APP_VERSION = "1.0"
DB_PATH = "data/shop.db"

# Roles
ROLE_ADMIN = "admin"
ROLE_STAFF = "staff"

# Payment modes
PAYMENT_MODES = ["Cash", "UPI", "Credit", "Cheque"]

# Product categories (add your own)
PRODUCT_CATEGORIES = [
    "Fertilizer", "Urea", "DAP", "NPK", "MOP", "SSP",
    "Organic", "Bio-fertilizer", "Micronutrient",
    "Pesticide", "Herbicide", "Fungicide", "Seeds", "Other"
]
# Units of measurement
PRODUCT_UNITS = ["Kg", "Gram", "Litre", "ML", "Bag", "Bottle", "Box"]

# ── GST CONFIGURATION ─────────────────────────────────────────
# ── GST CONFIGURATION ─────────────────────────────────────────
SHOP_GSTIN = "37XXXXX0000X1ZX"       # ← Replace with your actual GSTIN
SHOP_NAME = "Your Shop Name Here"     # ← Replace with your shop name
SHOP_ADDRESS = "Your Address Here"    # ← Replace with your address
SHOP_PHONE = "9999999999"             # ← Replace with your phone
SHOP_STATE = "Andhra Pradesh"
SHOP_STATE_CODE = "37"

# HSN codes and GST rates
# Format: "category": (hsn_code, gst_rate_percent)
HSN_GST_MAP = {
    "Fertilizer":       ("31059090", 5),
    "Urea":             ("31021000", 5),
    "DAP":              ("31053000", 5),
    "NPK":              ("31052000", 5),
    "MOP":              ("31042010", 5),
    "SSP":              ("31031000", 5),
    "Organic":          ("31010000", 5),
    "Bio-fertilizer":   ("31010000", 5),
    "Micronutrient":    ("31059090", 5),
    "Pesticide":        ("38081000", 18),
    "Herbicide":        ("38083000", 18),
    "Fungicide":        ("38082000", 18),
    "Seeds":            ("12099900", 0),
    "Other":            ("31059090", 5),
}

# Payment modes
PAYMENT_MODES = ["Cash", "UPI", "Credit", "Cheque", "Kisan Credit Card"]

# Product units
PRODUCT_UNITS = ["Kg", "Gram", "Litre", "ML", "Bag (45kg)",
                 "Bag (50kg)", "Bottle", "Box", "Packet"]

# Subscription / License settings
LICENSE_OWNER      = "Your Father's Name"
LICENSE_SHOP       = "Your Shop Name"
LICENSE_START_DATE = "2025-01-01"   # when you first installed
LICENSE_EXPIRY     = "2026-12-31"   # set your renewal date
LICENSE_TYPE       = "Full License" # Full License / Trial / Basic
SOFTWARE_VERSION   = "1.0.0"
SUPPORT_PHONE      = "9999999999"   # your number for backup
SUPPORT_EMAIL      = "your@email.com"

