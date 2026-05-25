import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
DATABASE_PATH = os.path.join(DATA_DIR, 'database.db')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, 'aadhaar'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, 'pan'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, 'address'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, 'lpg'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, 'cheque'), exist_ok=True)

SECRET_KEY = 'bpcl_sambalpur_png_secret_key'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'  # Simple configurable credentials
