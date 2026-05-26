import os
import psycopg2
import psycopg2.extras
import sqlite3
import config

def get_db_connection():
    if config.DATABASE_URL:
        conn = psycopg2.connect(config.DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect(config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def get_db_cursor(conn):
    if hasattr(conn, 'row_factory'):
        # SQLite
        return conn.cursor()
    else:
        # PostgreSQL
        return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def execute_query(cursor, query, params=None):
    """
    Executes a query by automatically converting placeholders between SQLite (?) and PostgreSQL (%s)
    depending on the active database driver.
    """
    if params is None:
        params = ()
    
    # Check if the cursor is SQLite
    is_sqlite = 'sqlite3' in type(cursor).__module__
    
    if is_sqlite:
        # Translate %s to ?
        query = query.replace('%s', '?')
    else:
        # Translate ? to %s
        query = query.replace('?', '%s')
        
    cursor.execute(query, params)
    return cursor

def init_db():
    conn = get_db_connection()
    cursor = get_db_cursor(conn)
    
    is_sqlite = hasattr(conn, 'row_factory')
    
    id_type = "INTEGER PRIMARY KEY AUTOINCREMENT" if is_sqlite else "SERIAL PRIMARY KEY"
    
    # Create consumers table
    query = f'''
    CREATE TABLE IF NOT EXISTS consumers (
        id {id_type},
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
        
        -- Document file paths (local path or Supabase URL)
        aadhaar_file TEXT,
        pan_file TEXT,
        address_file TEXT,
        lpg_file TEXT,
        cheque_file TEXT,
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    '''
    cursor.execute(query)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
