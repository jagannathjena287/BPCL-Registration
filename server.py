import os
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, send_file
import sqlite3
from werkzeug.utils import secure_filename
import config
from database import get_db_connection
from excel_export import export_to_excel
from datetime import datetime

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_DIR

# Custom function to check allowed extensions (PDF, PNG, JPG, JPEG)
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper to save uploaded files
def save_uploaded_file(file, doc_type, form_no):
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        # Clean form_no for filename safety
        safe_form_no = "".join(c for c in form_no if c.isalnum() or c in ('-', '_'))
        filename = f"{safe_form_no}_{doc_type}.{ext}"
        dest_dir = os.path.join(config.UPLOAD_DIR, doc_type)
        os.makedirs(dest_dir, exist_ok=True)
        filepath = os.path.join(dest_dir, filename)
        file.save(filepath)
        # return relative path to serve it via uploads route
        return f"{doc_type}/{filename}"
    return None

# Serve Frontend Pages
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/admin')
def admin_page():
    if 'logged_in' not in session:
        return redirect(url_for('login_view'))
    return send_from_directory('static', 'admin.html')

@app.route('/login')
def login_view():
    if 'logged_in' in session:
        return redirect(url_for('admin_page'))
    return send_from_directory('static', 'login.html')

# Admin Authentication Endpoints
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    
    if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
        session['logged_in'] = True
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST', 'GET'])
def api_logout():
    session.pop('logged_in', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/auth-check', methods=['GET'])
def api_auth_check():
    if 'logged_in' in session:
        return jsonify({'authenticated': True})
    return jsonify({'authenticated': False}), 401

# Serve Uploaded files securely
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
    return send_from_directory(config.UPLOAD_DIR, filename)

# API Dashboard stats
@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) as total FROM consumers")
    total = cursor.fetchone()['total']
    
    # Get total with Meter No
    cursor.execute("SELECT COUNT(*) as metered FROM consumers WHERE meter_no IS NOT NULL AND meter_no != ''")
    metered = cursor.fetchone()['metered']
    
    # Get property type distribution
    cursor.execute("SELECT type_of_property, COUNT(*) as count FROM consumers GROUP BY type_of_property")
    property_types = {r['type_of_property']: r['count'] for r in cursor.fetchall() if r['type_of_property']}
    
    # Get ownership type distribution
    cursor.execute("SELECT type_of_ownership, COUNT(*) as count FROM consumers GROUP BY type_of_ownership")
    ownership_types = {r['type_of_ownership']: r['count'] for r in cursor.fetchall() if r['type_of_ownership']}
    
    # Get recent 5 registrations
    cursor.execute("SELECT id, name, application_form_no, mobile_phone, created_at, meter_no FROM consumers ORDER BY id DESC LIMIT 5")
    recent = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'total': total,
        'metered': metered,
        'unmetered': total - metered,
        'property_types': property_types,
        'ownership_types': ownership_types,
        'recent': recent
    })

# Register a Consumer
@app.route('/api/register', methods=['POST'])
def api_register():
    # Fields are in form-data since we upload files
    form_data = request.form
    
    # Verify unique application number
    app_form_no = form_data.get('application_form_no')
    if not app_form_no:
        return jsonify({'success': False, 'message': 'Application Form Number is required.'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM consumers WHERE application_form_no = ?", (app_form_no,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': f'Application Form Number {app_form_no} already exists.'}), 400
    
    # Parse and save files
    aadhaar_file = save_uploaded_file(request.files.get('aadhaar_file'), 'aadhaar', app_form_no)
    pan_file = save_uploaded_file(request.files.get('pan_file'), 'pan', app_form_no)
    address_file = save_uploaded_file(request.files.get('address_file'), 'address', app_form_no)
    lpg_file = save_uploaded_file(request.files.get('lpg_file'), 'lpg', app_form_no)
    cheque_file = save_uploaded_file(request.files.get('cheque_file'), 'cheque', app_form_no)
    
    # Prepare data for insertion
    # Auto-generate full name
    first_name = form_data.get('first_name', '').strip()
    middle_name = form_data.get('middle_name', '').strip()
    last_name = form_data.get('last_name', '').strip()
    
    full_name_parts = [first_name]
    if middle_name:
        full_name_parts.append(middle_name)
    if last_name:
        full_name_parts.append(last_name)
    full_name = " ".join(full_name_parts)
    
    # Address field compilation (combine details for the address column)
    house_no = form_data.get('house_no', '').strip()
    street_no = form_data.get('street_no', '').strip()
    locality = form_data.get('locality', '').strip()
    landmark = form_data.get('landmark', '').strip()
    city = form_data.get('city', 'Sambalpur').strip()
    postal_code = form_data.get('postal_code', '').strip()
    
    address_parts = []
    if house_no: address_parts.append(f"H.No: {house_no}")
    if street_no: address_parts.append(street_no)
    if landmark: address_parts.append(f"Near {landmark}")
    if locality: address_parts.append(locality)
    address_parts.append(city)
    if postal_code: address_parts.append(postal_code)
    compiled_address = ", ".join(address_parts)
    
    # Split Aadhaar into 3 parts
    aadhaar_num = form_data.get('aadhaar_num', '').replace(' ', '').replace('-', '')
    aadhaar1, aadhaar2, aadhaar3 = '', '', ''
    if len(aadhaar_num) == 12:
        aadhaar1 = aadhaar_num[0:4]
        aadhaar2 = aadhaar_num[4:8]
        aadhaar3 = aadhaar_num[8:12]
        
    db_fields = {
        'name': full_name,
        'customer_group': form_data.get('customer_group', '01 - DOMESTIC'),
        'tel1': form_data.get('tel1', ''),
        'tel2': form_data.get('tel2', ''),
        'fax': form_data.get('fax', ''),
        'mobile_phone': form_data.get('mobile_phone', ''),
        'email': form_data.get('email', ''),
        'application_form_no': app_form_no,
        'geographical_area': form_data.get('geographical_area', 'CGD - Sambalpur'),
        'charge_area': form_data.get('charge_area', 'Sambalpur'),
        'locality': locality,
        'aadhaar1': aadhaar1,
        'aadhaar2': aadhaar2,
        'aadhaar3': aadhaar3,
        'aadhar_name': form_data.get('aadhar_name', full_name),
        'contact_title': form_data.get('contact_title', 'Mr'),
        'first_name': first_name,
        'middle_name': middle_name,
        'last_name': last_name,
        'father_name': form_data.get('father_name', ''),
        'designation': form_data.get('designation', ''),
        'address': compiled_address,
        'telephone1': form_data.get('telephone1', ''),
        'telephone2': form_data.get('telephone2', ''),
        'contact_mobile': form_data.get('contact_mobile', ''),
        'contact_email': form_data.get('contact_email', ''),
        'date_of_birth': form_data.get('date_of_birth', ''),
        'gender': form_data.get('gender', 'Male'),
        'profession': form_data.get('profession', ''),
        'house_no': house_no,
        'street_no': street_no,
        'po_box': form_data.get('po_box', ''),
        'postal_code': postal_code,
        'city': city,
        'gstin': form_data.get('gstin', ''),
        'gst_type': form_data.get('gst_type', ''),
        'type_of_property': form_data.get('type_of_property', 'ROW HOUSE'),
        'type_of_ownership': form_data.get('type_of_ownership', 'SELF OWNED'),
        'pan': form_data.get('pan', '').upper(),
        'customer_no': form_data.get('customer_no', ''),
        'distributor_name': form_data.get('distributor_name', ''),
        'omc_name': form_data.get('omc_name', ''),
        'scheme_code': form_data.get('scheme_code', 'PNG-DOM-08'),
        'cheque_no': form_data.get('cheque_no', ''),
        'cheque_date': form_data.get('cheque_date', ''),
        'cheque_received_date': form_data.get('cheque_received_date', ''),
        'cheque_amount': form_data.get('cheque_amount', '0'),
        'bank_name': form_data.get('bank_name', ''),
        'meter_no': form_data.get('meter_no', ''),
        
        # Files
        'aadhaar_file': aadhaar_file,
        'pan_file': pan_file,
        'address_file': address_file,
        'lpg_file': lpg_file,
        'cheque_file': cheque_file
    }
    
    # Build insert query dynamically
    keys = list(db_fields.keys())
    placeholders = ', '.join('?' for _ in keys)
    columns = ', '.join(keys)
    query = f"INSERT INTO consumers ({columns}) VALUES ({placeholders})"
    values = [db_fields[k] for k in keys]
    
    try:
        cursor.execute(query, values)
        conn.commit()
        consumer_id = cursor.lastrowid
        conn.close()
        return jsonify({
            'success': True,
            'message': 'Registration submitted successfully!',
            'id': consumer_id
        })
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Error inserting record: {str(e)}'}), 500

# Get list of consumers
@app.route('/api/consumers', methods=['GET'])
def get_consumers():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
        
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all') # 'all', 'metered', 'unmetered'
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM consumers WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE ? OR application_form_no LIKE ? OR mobile_phone LIKE ? OR locality LIKE ?)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param, search_param])
        
    if status_filter == 'metered':
        query += " AND meter_no IS NOT NULL AND meter_no != ''"
    elif status_filter == 'unmetered':
        query += " AND (meter_no IS NULL OR meter_no = '')"
        
    query += " ORDER BY id DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(r) for r in rows])

# Get individual consumer
@app.route('/api/consumers/<int:consumer_id>', methods=['GET'])
def get_consumer_by_id(consumer_id):
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM consumers WHERE id = ?", (consumer_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify(dict(row))
    return jsonify({'error': 'Consumer not found'}), 404

# Update consumer (e.g. to update Meter No)
@app.route('/api/consumers/<int:consumer_id>', methods=['PUT'])
def update_consumer(consumer_id):
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.json or {}
    meter_no = data.get('meter_no', '').strip()
    locality = data.get('locality', '').strip()
    mobile_phone = data.get('mobile_phone', '').strip()
    email = data.get('email', '').strip()
    scheme_code = data.get('scheme_code', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if consumer exists
    cursor.execute("SELECT id FROM consumers WHERE id = ?", (consumer_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Consumer not found'}), 404
        
    # Update fields
    cursor.execute('''
        UPDATE consumers 
        SET meter_no = ?, locality = ?, mobile_phone = ?, email = ?, scheme_code = ?
        WHERE id = ?
    ''', (meter_no, locality, mobile_phone, email, scheme_code, consumer_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Consumer details updated successfully'})

# Export to Excel
@app.route('/api/export', methods=['GET'])
def export_data():
    if 'logged_in' not in session:
        return redirect(url_for('login_view'))
        
    # Optional filtering: list of ids to export
    ids_str = request.args.get('ids', '')
    consumer_ids = [int(i) for i in ids_str.split(',') if i.strip().isdigit()] if ids_str else None
    
    # Create temp export path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_filename = f"BPCL_PNG_Sambalpur_Export_{timestamp}.xlsx"
    export_path = os.path.join(config.DATA_DIR, export_filename)
    
    try:
        count = export_to_excel(export_path, consumer_ids)
        if count == 0:
            return "No records to export", 400
            
        return send_file(
            export_path,
            as_attachment=True,
            download_name=export_filename,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return f"Error during export: {str(e)}", 500

if __name__ == '__main__':
    # Build DB first
    from database import init_db
    init_db()
    
    app.run(host='0.0.0.0', port=8000, debug=True)
