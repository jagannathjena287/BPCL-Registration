import sqlite3
from config import DATABASE_PATH

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create consumers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consumers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        customer_group TEXT DEFAULT '01 - DOMESTIC',
        tel1 TEXT,
        tel2 TEXT,
        fax TEXT,
        mobile_phone TEXT,
        email TEXT,
        application_form_no TEXT UNIQUE,
        geographical_area TEXT DEFAULT 'CGD - Sambalpur',
        charge_area TEXT DEFAULT 'Sambalpur',
        locality TEXT,
        aadhaar1 TEXT,
        aadhaar2 TEXT,
        aadhaar3 TEXT,
        aadhar_name TEXT,
        contact_title TEXT,
        first_name TEXT,
        middle_name TEXT,
        last_name TEXT,
        father_name TEXT,
        designation TEXT,
        address TEXT,
        telephone1 TEXT,
        telephone2 TEXT,
        contact_mobile TEXT,
        contact_email TEXT,
        date_of_birth TEXT,
        gender TEXT,
        profession TEXT,
        house_no TEXT,
        street_no TEXT,
        po_box TEXT,
        postal_code TEXT,
        city TEXT DEFAULT 'Sambalpur',
        gstin TEXT,
        gst_type TEXT,
        type_of_property TEXT,
        type_of_ownership TEXT,
        pan TEXT,
        customer_no TEXT,
        distributor_name TEXT,
        omc_name TEXT,
        scheme_code TEXT DEFAULT 'PNG-DOM-08',
        cheque_no TEXT,
        cheque_date TEXT,
        cheque_received_date TEXT,
        cheque_amount TEXT,
        bank_name TEXT,
        meter_no TEXT,
        
        -- Document file paths
        aadhaar_file TEXT,
        pan_file TEXT,
        address_file TEXT,
        lpg_file TEXT,
        cheque_file TEXT,
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
