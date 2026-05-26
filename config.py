import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Supabase Configurations
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Fallback local configurations (for development)
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
DATABASE_PATH = os.path.join(DATA_DIR, 'database.db')

# Ensure directories exist (only when no remote database is configured)
if not DATABASE_URL:
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_DIR, 'aadhaar'), exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_DIR, 'pan'), exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_DIR, 'address'), exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_DIR, 'lpg'), exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_DIR, 'cheque'), exist_ok=True)

SECRET_KEY = os.environ.get('SECRET_KEY', 'bpcl_sambalpur_png_secret_key')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'password123')
