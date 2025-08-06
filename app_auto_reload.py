from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
from datetime import datetime, timedelta
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
import json
import pandas as pd
from io import BytesIO
import base64
import requests
from urllib.parse import urlencode

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Environment variables loaded successfully")
except ImportError:
    print("⚠ python-dotenv not available, using default values")

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Enhanced development configuration
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Azure SQL Database configuration from environment variables
AZURE_SQL_CONFIG = {
    'server': os.getenv('DB_SERVER', 'legexzt-server.database.windows.net'),
    'database': os.getenv('DB_NAME', 'legezt-app'),
    'username': os.getenv('DB_USER', 'iamlegezt'),
    'password': os.getenv('DB_PASS', 'mehonjibraan_09'),
    'port': int(os.getenv('DB_PORT', 1433))
}

# Email configuration from environment variables
EMAIL_CONFIG = {
    'server': os.getenv('MAIL_SERVER', 'smtp.privateemail.com'),
    'port': int(os.getenv('MAIL_PORT', 587)),
    'use_tls': os.getenv('MAIL_USE_TLS', 'True').lower() == 'true',
    'username': os.getenv('EMAIL_USER', 'mohdjibraan@legezthub.me'),
    'password': os.getenv('EMAIL_PASS', 'iamlegezt09')
}

# Admin email for verification
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'mdjibjibran@gmail.com')

# Google Drive API Configuration - Direct Storage System
GOOGLE_DRIVE_CONFIG = {
    'client_id': os.getenv('GOOGLE_DRIVE_CLIENT_ID', ''),
    'client_secret': os.getenv('GOOGLE_DRIVE_CLIENT_SECRET', ''),
    'redirect_uri': os.getenv('GOOGLE_DRIVE_REDIRECT_URI', 'http://127.0.0.1:5000/oauth2callback'),
    'folder_name': os.getenv('GOOGLE_DRIVE_FOLDER_NAME', 'Legezt Portal'),
    'scopes': ['https://www.googleapis.com/auth/drive.file'],
    'admin_email': os.getenv('ADMIN_EMAIL', 'mdjibjibran@gmail.com'),
    'auto_connect': True  # Automatically connect without admin setup
}

# Global variable to store admin's access token
ADMIN_GOOGLE_DRIVE_TOKEN = None

# Token storage file
TOKEN_FILE = 'google_drive_tokens.json'

print(f"✓ Azure SQL config: {AZURE_SQL_CONFIG['server']}:{AZURE_SQL_CONFIG['port']}/{AZURE_SQL_CONFIG['database']}")
print(f"✓ Email config: {EMAIL_CONFIG['server']}:{EMAIL_CONFIG['port']}")
print(f"✓ Admin email: {ADMIN_EMAIL}")
print(f"✓ Google Drive folder: {GOOGLE_DRIVE_CONFIG['folder_name']}")
print(f"✓ Auto-reload enabled: {app.config['TEMPLATES_AUTO_RELOAD']}")

# Database connection function for Azure SQL
def get_db_connection():
    """Attempt to connect to Azure SQL Database"""
    try:
        import pyodbc
        
        # Try different ODBC drivers
        drivers = [
            '{ODBC Driver 18 for SQL Server}',
            '{ODBC Driver 17 for SQL Server}',
            '{SQL Server}',
            '{SQL Server Native Client 11.0}'
        ]
        
        for driver in drivers:
            try:
                connection_string = (
                    f"DRIVER={driver};"
                    f"SERVER={AZURE_SQL_CONFIG['server']};"
                    f"DATABASE={AZURE_SQL_CONFIG['database']};"
                    f"UID={AZURE_SQL_CONFIG['username']};"
                    f"PWD={AZURE_SQL_CONFIG['password']};"
                    f"Encrypt=yes;"
                    f"TrustServerCertificate=no;"
                    f"Connection Timeout=30;"
                )
                
                connection = pyodbc.connect(connection_string)
                print(f"✓ Azure SQL Database connected successfully using {driver}")
                return connection
            except pyodbc.Error as e:
                print(f"⚠ Driver {driver} failed: {e}")
                continue
        
        print("✗ All ODBC drivers failed")
        return None
        
    except ImportError:
        print("⚠ pyodbc not available")
        return None
    except Exception as e:
        print(f"✗ Azure SQL connection failed: {e}")
        return None

# Mock database (fallback if Azure SQL is not available)
def load_users():
    """Load users from JSON file"""
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"✗ Failed to load users: {e}")
        return {}

def save_users(users_data):
    """Save users to JSON file"""
    try:
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Users saved to users.json")
    except Exception as e:
        print(f"✗ Failed to save users: {e}")

def load_admin_verifications():
    """Load admin verifications from JSON file"""
    try:
        with open('admin_verifications.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"✗ Failed to load admin verifications: {e}")
        return {}

def save_admin_verifications(verifications_data):
    """Save admin verifications to JSON file"""
    try:
        with open('admin_verifications.json', 'w', encoding='utf-8') as f:
            json.dump(verifications_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Admin verifications saved to admin_verifications.json")
    except Exception as e:
        print(f"✗ Failed to save admin verifications: {e}")

# Load data from files on startup
users = load_users()
admin_verifications = load_admin_verifications()

def load_files():
    """Load files from JSON file"""
    try:
        with open('files.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"✗ Failed to load files: {e}")
        return []

def save_files(files_data):
    """Save files to JSON file"""
    try:
        with open('files.json', 'w', encoding='utf-8') as f:
            json.dump(files_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Files saved to files.json")
    except Exception as e:
        print(f"✗ Failed to save files: {e}")

# Load files from file on startup
files = load_files()

# College Management System Data
def load_colleges():
    """Load colleges from JSON file"""
    try:
        with open('colleges.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"✗ Failed to load colleges: {e}")
        return []

def save_colleges(colleges_data):
    """Save colleges to JSON file"""
    try:
        with open('colleges.json', 'w', encoding='utf-8') as f:
            json.dump(colleges_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Colleges saved to colleges.json")
    except Exception as e:
        print(f"✗ Failed to save colleges: {e}")

# Load colleges from file on startup
colleges = load_colleges()

def load_branches():
    """Load branches from JSON file"""
    try:
        with open('branches.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default branches if file doesn't exist
        return [
            {'id': 1, 'name': 'Engineering', 'description': 'Engineering branches', 'subjects': ['Computer Science', 'Mechanical Engineering', 'Electrical Engineering']},
            {'id': 2, 'name': 'Science', 'description': 'Science branches', 'subjects': ['Physics', 'Chemistry', 'Mathematics', 'Biology']},
            {'id': 3, 'name': 'Arts', 'description': 'Arts branches', 'subjects': ['English', 'History', 'Literature', 'Philosophy']},
            {'id': 4, 'name': 'Commerce', 'description': 'Commerce branches', 'subjects': ['Economics', 'Business Administration', 'Accounting', 'Finance']}
        ]
    except Exception as e:
        print(f"✗ Failed to load branches: {e}")
        return []

def save_branches(branches_data):
    """Save branches to JSON file"""
    try:
        with open('branches.json', 'w', encoding='utf-8') as f:
            json.dump(branches_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Branches saved to branches.json")
    except Exception as e:
        print(f"✗ Failed to save branches: {e}")

# Load branches from file on startup
branches = load_branches()

def load_subjects():
    """Load subjects from JSON file"""
    try:
        with open('subjects.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default subjects if file doesn't exist
        default_subjects = [
            {'id': 1, 'name': 'Computer Science', 'description': 'Computer Science fundamentals'},
            {'id': 2, 'name': 'Mathematics', 'description': 'Mathematical concepts and applications'},
            {'id': 3, 'name': 'Physics', 'description': 'Physics principles and theories'},
            {'id': 4, 'name': 'Chemistry', 'description': 'Chemical processes and reactions'},
            {'id': 5, 'name': 'English', 'description': 'English language and literature'},
            {'id': 6, 'name': 'Economics', 'description': 'Economic theories and principles'}
        ]
        save_subjects(default_subjects)
        return default_subjects
    except Exception as e:
        print(f"✗ Failed to load subjects: {e}")
        return []

def save_subjects(subjects_data):
    """Save subjects to JSON file"""
    try:
        with open('subjects.json', 'w') as f:
            json.dump(subjects_data, f, indent=2)
        print(f"✓ Subjects saved to subjects.json")
    except Exception as e:
        print(f"✗ Failed to save subjects: {e}")

years = [
    {'id': 1, 'name': '1st Year', 'semesters': [{'id': 1, 'name': '1st Semester'}, {'id': 2, 'name': '2nd Semester'}]},
    {'id': 2, 'name': '2nd Year', 'semesters': [{'id': 3, 'name': '3rd Semester'}, {'id': 4, 'name': '4th Semester'}]},
    {'id': 3, 'name': '3rd Year', 'semesters': [{'id': 5, 'name': '5th Semester'}, {'id': 6, 'name': '6th Semester'}]},
    {'id': 4, 'name': '4th Year', 'semesters': [{'id': 7, 'name': '7th Semester'}, {'id': 8, 'name': '8th Semester'}]}
]

# Enhanced branch and subject management (now loaded from file)

# Load subjects from file on startup
subjects = load_subjects()

# New branch structure functions
def load_branch_structure():
    """Load branch structure with separate data for each year/semester"""
    try:
        with open('branch_structure.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"years": {}}

def get_branches_for_semester(year_id, semester_id):
    """Get branches for specific year/semester"""
    structure = load_branch_structure()
    year_key = str(year_id)
    semester_key = str(semester_id)
    
    if (year_key in structure["years"] and 
        semester_key in structure["years"][year_key]["semesters"]):
        return structure["years"][year_key]["semesters"][semester_key]["branches"]
    return []

def save_branch_structure(structure):
    """Save branch structure"""
    with open('branch_structure.json', 'w') as f:
        json.dump(structure, f, indent=2)

def get_branch_by_id(branch_id, year_id, semester_id):
    """Get a specific branch by ID for a year/semester"""
    branches = get_branches_for_semester(year_id, semester_id)
    return next((b for b in branches if b['id'] == branch_id), None)

def update_branch_in_semester(year_id, semester_id, branch_id, updated_data):
    """Update a branch in a specific semester"""
    structure = load_branch_structure()
    year_key = str(year_id)
    semester_key = str(semester_id)
    
    if (year_key in structure["years"] and 
        semester_key in structure["years"][year_key]["semesters"]):
        
        branches = structure["years"][year_key]["semesters"][semester_key]["branches"]
        for i, branch in enumerate(branches):
            if branch['id'] == branch_id:
                branches[i].update(updated_data)
                save_branch_structure(structure)
                return True
    return False

def generate_access_code():
    return ''.join(random.choices(string.digits, k=6))

def send_email(to_email, subject, body):
    """Attempt to send email using configured SMTP"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['username']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['server'], EMAIL_CONFIG['port'])
        if EMAIL_CONFIG['use_tls']:
            server.starttls()
        
        server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
        server.send_message(msg)
        server.quit()
        
        print(f"✓ Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"✗ Email sending failed: {e}")
        return False

def save_to_file(data, filename):
    """Save data to JSON file as backup"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Data saved to {filename}")
    except Exception as e:
        print(f"✗ Failed to save to {filename}: {e}")

def load_from_file(filename):
    """Load data from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"✗ Failed to load from {filename}: {e}")
        return {}

# Google Drive API Functions
def get_google_drive_auth_url():
    """Generate Google Drive OAuth2 authorization URL for admin account"""
    params = {
        'client_id': GOOGLE_DRIVE_CONFIG['client_id'],
        'redirect_uri': GOOGLE_DRIVE_CONFIG['redirect_uri'],
        'scope': ' '.join(GOOGLE_DRIVE_CONFIG['scopes']),
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent',
        'login_hint': GOOGLE_DRIVE_CONFIG['admin_email']  # Force admin account login
    }
    return f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"

def get_google_drive_tokens(auth_code):
    """Exchange authorization code for access and refresh tokens"""
    try:
        token_url = 'https://oauth2.googleapis.com/token'
        data = {
            'client_id': GOOGLE_DRIVE_CONFIG['client_id'],
            'client_secret': GOOGLE_DRIVE_CONFIG['client_secret'],
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': GOOGLE_DRIVE_CONFIG['redirect_uri']
        }
        
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            tokens = response.json()
            print(f"✓ Successfully obtained tokens from Google")
            return tokens
        else:
            print(f"✗ Failed to get tokens: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error getting tokens: {e}")
        return None

def refresh_google_drive_token():
    """Refresh Google Drive access token"""
    try:
        refresh_token = session.get('google_drive_refresh_token')
        if not refresh_token:
            return False
            
        token_url = 'https://oauth2.googleapis.com/token'
        data = {
            'client_id': GOOGLE_DRIVE_CONFIG['client_id'],
            'client_secret': GOOGLE_DRIVE_CONFIG['client_secret'],
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            tokens = response.json()
            session['google_drive_access_token'] = tokens.get('access_token')
            return True
        else:
            print(f"✗ Failed to refresh token: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error refreshing token: {e}")
        return False

def get_or_create_legezt_folder():
    """Get or create the Legezt Portal folder in Google Drive"""
    global ADMIN_GOOGLE_DRIVE_TOKEN
    
    try:
        # Ensure we have valid tokens
        if not ensure_google_drive_connected():
            return None
            
        access_token = ADMIN_GOOGLE_DRIVE_TOKEN.get('access_token')
        if not access_token:
            return None
            
        # First, try to find existing folder
        search_url = 'https://www.googleapis.com/drive/v3/files'
        params = {
            'q': f"name='{GOOGLE_DRIVE_CONFIG['folder_name']}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            'access_token': access_token
        }
        
        response = requests.get(search_url, params=params)
        if response.status_code == 200:
            files = response.json().get('files', [])
            if files:
                return files[0]['id']  # Return existing folder ID
        
        # Create new folder if not found
        create_url = 'https://www.googleapis.com/drive/v3/files'
        folder_data = {
            'name': GOOGLE_DRIVE_CONFIG['folder_name'],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(create_url, json=folder_data, headers=headers)
        if response.status_code == 200:
            folder = response.json()
            print(f"✓ Created Google Drive folder: {folder['name']} (ID: {folder['id']})")
            return folder['id']
        else:
            print(f"✗ Failed to create folder: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error with Google Drive folder: {e}")
        return None

def upload_file_to_drive(file_data, filename, folder_id=None):
    """Upload file to Google Drive"""
    global ADMIN_GOOGLE_DRIVE_TOKEN
    
    try:
        # Ensure we have valid tokens
        if not ensure_google_drive_connected():
            return None
            
        access_token = ADMIN_GOOGLE_DRIVE_TOKEN.get('access_token')
        if not access_token:
            return None
            
        # Get or create folder
        if not folder_id:
            folder_id = get_or_create_legezt_folder()
            if not folder_id:
                return None
        
        # Upload file using resumable upload for better reliability
        upload_url = 'https://www.googleapis.com/upload/drive/v3/files'
        params = {
            'uploadType': 'resumable',
            'access_token': access_token
        }
        
        # Prepare metadata
        metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        
        # Step 1: Initialize upload session
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Upload-Content-Type': 'application/octet-stream',
            'X-Upload-Content-Length': str(len(file_data))
        }
        
        response = requests.post(upload_url, params=params, json=metadata, headers=headers)
        if response.status_code != 200:
            print(f"✗ Failed to initialize upload: {response.text}")
            return None
            
        # Get the upload URL from the response
        upload_session_url = response.headers.get('Location')
        if not upload_session_url:
            print("✗ No upload session URL received")
            return None
        
        # Step 2: Upload the file data
        upload_headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(len(file_data))
        }
        
        response = requests.put(upload_session_url, data=file_data, headers=upload_headers)
        if response.status_code == 200:
            file_info = response.json()
            print(f"✓ File uploaded to Google Drive: {file_info['name']} (ID: {file_info['id']})")
            return {
                'id': file_info['id'],
                'name': file_info['name'],
                'webViewLink': file_info.get('webViewLink'),
                'webContentLink': file_info.get('webContentLink')
            }
        else:
            print(f"✗ Failed to upload file: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error uploading to Google Drive: {e}")
        return None

def create_shareable_link(file_id):
    """Create a shareable link for a Google Drive file"""
    global ADMIN_GOOGLE_DRIVE_TOKEN
    
    try:
        # Ensure we have valid tokens
        if not ensure_google_drive_connected():
            return None
            
        access_token = ADMIN_GOOGLE_DRIVE_TOKEN.get('access_token')
        if not access_token:
            return None
            
        # Set file permissions to anyone with link can view
        permissions_url = f'https://www.googleapis.com/drive/v3/files/{file_id}/permissions'
        permission_data = {
            'role': 'reader',
            'type': 'anyone'
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(permissions_url, json=permission_data, headers=headers)
        if response.status_code == 200:
            # Get the file info to return the web view link
            file_url = f'https://www.googleapis.com/drive/v3/files/{file_id}'
            params = {
                'fields': 'webViewLink,webContentLink',
                'access_token': access_token
            }
            
            file_response = requests.get(file_url, params=params)
            if file_response.status_code == 200:
                file_info = file_response.json()
                return file_info.get('webViewLink')
        
        return None
        
    except Exception as e:
        print(f"✗ Error creating shareable link: {e}")
        return None

# Load existing data from files (fallback)
users = load_from_file('users.json')
admin_verifications = load_from_file('admin_verifications.json')
login_history = load_from_file('login_history.json')

# Load and save functions for subjects


@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/home')
def home():
    # If user is already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/college')
def college():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('college_notes.html', files=files, colleges=colleges)

@app.route('/college/add', methods=['GET', 'POST'])
def add_college():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('college'))
    
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        description = request.form['description']
        
        # Generate unique ID
        new_id = 1
        if colleges:
            new_id = max(c['id'] for c in colleges) + 1
        
        new_college = {
            'id': new_id,
            'name': name,
            'location': location,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'created_by': session['user_id']
        }
        
        colleges.append(new_college)
        save_colleges(colleges)  # Save to file
        flash('College added successfully!', 'success')
        return redirect(url_for('college'))
    
    return render_template('add_college.html')

@app.route('/college/edit/<int:college_id>', methods=['GET', 'POST'])
def edit_college(college_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('college'))
    
    college = next((c for c in colleges if c['id'] == college_id), None)
    if not college:
        flash('College not found.', 'error')
        return redirect(url_for('college'))
    
    if request.method == 'POST':
        college['name'] = request.form['name']
        college['location'] = request.form['location']
        college['description'] = request.form['description']
        college['updated_at'] = datetime.now().isoformat()
        
        save_colleges(colleges)  # Save to file
        flash('College updated successfully!', 'success')
        return redirect(url_for('college'))
    
    return render_template('edit_college.html', college=college)

@app.route('/college/delete/<int:college_id>', methods=['POST'])
def delete_college(college_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('college'))
    
    global colleges
    colleges = [c for c in colleges if c['id'] != college_id]
    save_colleges(colleges)  # Save to file
    flash('College deleted successfully!', 'success')
    return redirect(url_for('college'))

@app.route('/college/<int:college_id>')
def college_detail(college_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    college = next((c for c in colleges if c['id'] == college_id), None)
    if not college:
        flash('College not found.', 'error')
        return redirect(url_for('college'))
    
    return render_template('college_detail.html', college=college, years=years)

@app.route('/college/<int:college_id>/year/<int:year_id>')
def college_year(college_id, year_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    college = next((c for c in colleges if c['id'] == college_id), None)
    year = next((y for y in years if y['id'] == year_id), None)
    
    if not college or not year:
        flash('College or year not found.', 'error')
        return redirect(url_for('college'))
    
    return render_template('college_year.html', college=college, year=year)

@app.route('/college/<int:college_id>/year/<int:year_id>/semester/<int:semester_id>')
def college_semester(college_id, year_id, semester_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    college = next((c for c in colleges if c['id'] == college_id), None)
    year = next((y for y in years if y['id'] == year_id), None)
    semester = None
    
    if year:
        semester = next((s for s in year['semesters'] if s['id'] == semester_id), None)
    
    if not college or not year or not semester:
        flash('College, year, or semester not found.', 'error')
        return redirect(url_for('college'))
    
    # Get branches for this specific semester using new structure
    semester_branches = get_branches_for_semester(year_id, semester_id)
    
    return render_template('college_semester.html', college=college, year=year, semester=semester, branches=semester_branches)

@app.route('/college/<int:college_id>/year/<int:year_id>/semester/<int:semester_id>/branch/<int:branch_id>')
def college_branch(college_id, year_id, semester_id, branch_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    college = next((c for c in colleges if c['id'] == college_id), None)
    year = next((y for y in years if y['id'] == year_id), None)
    semester = None
    
    # Get branch from specific semester using new structure
    branch = get_branch_by_id(branch_id, year_id, semester_id)
    
    if year:
        semester = next((s for s in year['semesters'] if s['id'] == semester_id), None)
    
    if not college or not year or not semester or not branch:
        flash('College, year, semester, or branch not found.', 'error')
        return redirect(url_for('college'))
    
    # Filter files by branch
    branch_files = [f for f in files if f.get('branch') == branch['name']]
    
    # Get branch subjects (convert from names to full subject objects)
    branch_subjects = []
    if 'subjects' in branch:
        for subject_name in branch['subjects']:
            subject_obj = next((s for s in subjects if s['name'] == subject_name), None)
            if subject_obj:
                branch_subjects.append(subject_obj)
    
    return render_template('college_branch.html', college=college, year=year, semester=semester, branch=branch, files=branch_files, subjects=branch_subjects)

@app.route('/college/<int:college_id>/year/<int:year_id>/semester/<int:semester_id>/branch/<int:branch_id>/subject/<subject_name>')
def college_subject(college_id, year_id, semester_id, branch_id, subject_name):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    college = next((c for c in colleges if c['id'] == college_id), None)
    year = next((y for y in years if y['id'] == year_id), None)
    semester = None
    
    # Get branch from specific semester using new structure
    branch = get_branch_by_id(branch_id, year_id, semester_id)
    
    if year:
        semester = next((s for s in year['semesters'] if s['id'] == semester_id), None)
    
    if not college or not year or not semester or not branch:
        flash('College, year, semester, or branch not found.', 'error')
        return redirect(url_for('college'))
    
    # Filter files by branch and subject
    subject_files = [f for f in files if f.get('branch') == branch['name'] and f.get('subject') == subject_name]
    
    return render_template('college_subject.html', college=college, year=year, semester=semester, branch=branch, subject=subject_name, files=subject_files)

# Branch Management Routes
@app.route('/college/<int:college_id>/year/<int:year_id>/semester/<int:semester_id>/branch/add', methods=['GET', 'POST'])
def add_branch(college_id, year_id, semester_id):
    global branches
    
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('college_semester', college_id=college_id, year_id=year_id, semester_id=semester_id))
    
    college = next((c for c in colleges if c['id'] == college_id), None)
    year = next((y for y in years if y['id'] == year_id), None)
    semester = None
    
    if year:
        semester = next((s for s in year['semesters'] if s['id'] == semester_id), None)
    
    if not college or not year or not semester:
        flash('College, year, or semester not found.', 'error')
        return redirect(url_for('college'))
    
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form['description'].strip()
        
        if not name:
            flash('Branch name is required.', 'error')
            return render_template('add_branch.html', college=college, year=year, semester=semester)
        
        # Get current semester branches to check for duplicates
        semester_branches = get_branches_for_semester(year_id, semester_id)
        
        # Check if branch name already exists in this semester
        if any(b['name'].lower() == name.lower() for b in semester_branches):
            flash('Branch with this name already exists in this semester.', 'error')
            return render_template('add_branch.html', college=college, year=year, semester=semester)
        
        # Generate new branch ID
        new_id = max([b['id'] for b in semester_branches], default=0) + 1
        if not semester_branches:  # If no branches in semester, start from 1
            new_id = 1
        
        # Add new branch to this specific semester
        new_branch = {
            'id': new_id,
            'name': name,
            'description': description,
            'year_id': year_id,
            'semester_id': semester_id,
            'subjects': [],
            'created_at': datetime.now().isoformat()
        }
        
        # Add to the specific semester
        structure = load_branch_structure()
        year_key = str(year_id)
        semester_key = str(semester_id)
        
        if (year_key in structure["years"] and 
            semester_key in structure["years"][year_key]["semesters"]):
            structure["years"][year_key]["semesters"][semester_key]["branches"].append(new_branch)
            save_branch_structure(structure)
        
        flash('Branch added successfully!', 'success')
        return redirect(url_for('college_semester', college_id=college_id, year_id=year_id, semester_id=semester_id))
    
    return render_template('add_branch.html', college=college, year=year, semester=semester)

@app.route('/college/<int:college_id>/year/<int:year_id>/semester/<int:semester_id>/branch/<int:branch_id>/edit', methods=['GET', 'POST'])
def edit_branch(college_id, year_id, semester_id, branch_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('college_semester', college_id=college_id, year_id=year_id, semester_id=semester_id))
    
    college = next((c for c in colleges if c['id'] == college_id), None)
    year = next((y for y in years if y['id'] == year_id), None)
    semester = None
    
    # Get branch from specific semester using new structure
    branch = get_branch_by_id(branch_id, year_id, semester_id)
    
    if year:
        semester = next((s for s in year['semesters'] if s['id'] == semester_id), None)
    
    if not college or not year or not semester or not branch:
        flash('College, year, semester, or branch not found.', 'error')
        return redirect(url_for('college'))
    
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form['description'].strip()
        
        if not name:
            flash('Branch name is required.', 'error')
            return render_template('edit_branch.html', college=college, year=year, semester=semester, branch=branch)
        
        # Get current semester branches to check for duplicates
        semester_branches = get_branches_for_semester(year_id, semester_id)
        
        # Check if branch name already exists in this semester (excluding current branch)
        if any(b['name'].lower() == name.lower() and b['id'] != branch_id for b in semester_branches):
            flash('Branch with this name already exists in this semester.', 'error')
            return render_template('edit_branch.html', college=college, year=year, semester=semester, branch=branch)
        
        # Update branch in the specific semester
        updated_data = {
            'name': name,
            'description': description
        }
        
        if update_branch_in_semester(year_id, semester_id, branch_id, updated_data):
            flash('Branch updated successfully!', 'success')
        else:
            flash('Failed to update branch.', 'error')
        return redirect(url_for('college_semester', college_id=college_id, year_id=year_id, semester_id=semester_id))
    
    return render_template('edit_branch.html', college=college, year=year, semester=semester, branch=branch)

@app.route('/college/<int:college_id>/year/<int:year_id>/semester/<int:semester_id>/branch/<int:branch_id>/delete', methods=['POST'])
def delete_branch(college_id, year_id, semester_id, branch_id):
    global branches
    
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('college_semester', college_id=college_id, year_id=year_id, semester_id=semester_id))
    
    branches = [b for b in branches if b['id'] != branch_id]
    save_branches(branches)  # Save to file
    
    flash('Branch deleted successfully!', 'success')
    return redirect(url_for('college_semester', college_id=college_id, year_id=year_id, semester_id=semester_id))

# Subject Management Routes
@app.route('/college/<int:college_id>/year/<int:year_id>/semester/<int:semester_id>/branch/<int:branch_id>/subject/add', methods=['GET', 'POST'])
def add_subject(college_id, year_id, semester_id, branch_id):
    """Add a new subject to a branch"""
    global subjects
    
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Find the college, year, semester, and branch
    college = next((c for c in colleges if c['id'] == college_id), None)
    year = next((y for y in years if y['id'] == year_id), None)
    semester = next((s for s in year['semesters'] if s['id'] == semester_id), None) if year else None
    
    # Get branch from specific semester using new structure
    branch = get_branch_by_id(branch_id, year_id, semester_id)
    
    if not all([college, year, semester, branch]):
        flash('Invalid college, year, semester, or branch.', 'error')
        return redirect(url_for('college'))
    
    if request.method == 'POST':
        subject_name = request.form['subject_name'].strip()
        subject_description = request.form['subject_description'].strip()
        
        if not subject_name:
            flash('Subject name is required.', 'error')
            return render_template('add_subject.html', college=college, year=year, semester=semester, branch=branch)
        
        # Check if subject already exists
        if any(s['name'].lower() == subject_name.lower() for s in subjects):
            flash('Subject with this name already exists.', 'error')
            return render_template('add_subject.html', college=college, year=year, semester=semester, branch=branch)
        
        # Generate unique ID for new subject
        new_id = max([s['id'] for s in subjects], default=0) + 1
        
        # Add new subject
        new_subject = {
            'id': new_id,
            'name': subject_name,
            'description': subject_description
        }
        subjects.append(new_subject)
        save_subjects(subjects)
        
        # Add subject to branch if not already present
        if 'subjects' not in branch:
            branch['subjects'] = []
        if subject_name not in branch['subjects']:
            branch['subjects'].append(subject_name)
            
            # Update the branch in the specific semester
            updated_data = {'subjects': branch['subjects']}
            update_branch_in_semester(year_id, semester_id, branch_id, updated_data)
        
        flash('Subject added successfully!', 'success')
        return redirect(url_for('college_branch', college_id=college_id, year_id=year_id, semester_id=semester_id, branch_id=branch_id))
    
    return render_template('add_subject.html', college=college, year=year, semester=semester, branch=branch)

@app.route('/college/<int:college_id>/year/<int:year_id>/semester/<int:semester_id>/branch/<int:branch_id>/subject/<int:subject_id>/edit', methods=['GET', 'POST'])
def edit_subject(college_id, year_id, semester_id, branch_id, subject_id):
    """Edit an existing subject"""
    global subjects
    
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Find the college, year, semester, branch, and subject
    college = next((c for c in colleges if c['id'] == college_id), None)
    year = next((y for y in years if y['id'] == year_id), None)
    semester = next((s for s in year['semesters'] if s['id'] == semester_id), None) if year else None
    
    # Get branch from specific semester using new structure
    branch = get_branch_by_id(branch_id, year_id, semester_id)
    subject = next((s for s in subjects if s['id'] == subject_id), None)
    
    if not all([college, year, semester, branch, subject]):
        flash('Invalid college, year, semester, branch, or subject.', 'error')
        return redirect(url_for('college'))
    
    if request.method == 'POST':
        subject_name = request.form['subject_name'].strip()
        subject_description = request.form['subject_description'].strip()
        
        if not subject_name:
            flash('Subject name is required.', 'error')
            return render_template('edit_subject.html', college=college, year=year, semester=semester, branch=branch, subject=subject)
        
        # Check if subject name already exists (excluding current subject)
        if any(s['name'].lower() == subject_name.lower() and s['id'] != subject_id for s in subjects):
            flash('Subject with this name already exists.', 'error')
            return render_template('edit_subject.html', college=college, year=year, semester=semester, branch=branch, subject=subject)
        
        # First, get the old name before we update the subject
        old_name = subject.get('name', '')
        
        # Update subject
        subject['name'] = subject_name
        subject['description'] = subject_description
        save_subjects(subjects)
        
        # Update subject name in branch if it exists there
        if 'subjects' in branch:
            # Remove old name if it exists
            if old_name in branch['subjects']:
                branch['subjects'].remove(old_name)
            # Add new name if it's not already there
            if subject_name not in branch['subjects']:
                branch['subjects'].append(subject_name)
            
            # Update the branch in the specific semester
            updated_data = {'subjects': branch['subjects']}
            update_branch_in_semester(year_id, semester_id, branch_id, updated_data)
        
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('college_branch', college_id=college_id, year_id=year_id, semester_id=semester_id, branch_id=branch_id))
    
    return render_template('edit_subject.html', college=college, year=year, semester=semester, branch=branch, subject=subject)

@app.route('/college/<int:college_id>/year/<int:year_id>/semester/<int:semester_id>/branch/<int:branch_id>/subject/<int:subject_id>/delete', methods=['POST'])
def delete_subject(college_id, year_id, semester_id, branch_id, subject_id):
    """Delete a subject"""
    global subjects
    
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Find the college, year, semester, branch, and subject
    college = next((c for c in colleges if c['id'] == college_id), None)
    year = next((y for y in years if y['id'] == year_id), None)
    semester = next((s for s in year['semesters'] if s['id'] == semester_id), None) if year else None
    
    # Get branch from specific semester using new structure
    branch = get_branch_by_id(branch_id, year_id, semester_id)
    subject = next((s for s in subjects if s['id'] == subject_id), None)
    
    if not all([college, year, semester, branch, subject]):
        flash('Invalid college, year, semester, branch, or subject.', 'error')
        return redirect(url_for('college'))
    # Remove subject from subjects list
    subjects = [s for s in subjects if s['id'] != subject_id]
    save_subjects(subjects)
    
    # Remove subject from branch if it exists there
    if 'subjects' in branch and subject['name'] in branch['subjects']:
        branch['subjects'].remove(subject['name'])
        
        # Update the branch in the specific semester
        updated_data = {'subjects': branch['subjects']}
        update_branch_in_semester(year_id, semester_id, branch_id, updated_data)
    
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('college_branch', college_id=college_id, year_id=year_id, semester_id=semester_id, branch_id=branch_id))

# Google Drive OAuth Routes
@app.route('/google-drive-auth')
def google_drive_auth():
    """Initiate Google Drive OAuth2 flow"""
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    auth_url = get_google_drive_auth_url()
    return redirect(auth_url)

@app.route('/oauth2callback')
def oauth2callback():
    """Handle Google Drive OAuth2 callback for admin account"""
    global ADMIN_GOOGLE_DRIVE_TOKEN
    
    auth_code = request.args.get('code')
    if not auth_code:
        flash('Authorization failed. Please try again.', 'error')
        return redirect(url_for('upload'))
    
    try:
        # Exchange code for tokens
        tokens = get_google_drive_tokens(auth_code)
        if tokens and tokens.get('access_token'):
            # Store admin tokens globally and persistently
            ADMIN_GOOGLE_DRIVE_TOKEN = tokens
            
            # Save tokens to persistent storage
            if save_google_drive_tokens(tokens):
                # Create or get the Legezt Portal folder
                folder_id = get_or_create_legezt_folder()
                if folder_id:
                    session['google_drive_folder_id'] = folder_id
                    flash('Google Drive connected successfully! System account is now permanently linked. All uploads will go to system\'s Google Drive.', 'success')
                else:
                    flash('Connected to Google Drive but failed to create folder.', 'warning')
            else:
                flash('Connected to Google Drive but failed to save authentication. Please try again.', 'warning')
        else:
            flash('Failed to get access tokens from Google.', 'error')
    except Exception as e:
        flash(f'Error connecting to Google Drive: {str(e)}', 'error')
    
    return redirect(url_for('upload'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if email in users and check_password_hash(users[email]['password'], password):
            session['user_id'] = email
            session['role'] = users[email]['role']
            
            # Track login history
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if email not in login_history:
                login_history[email] = []
            
            login_history[email].append({
                'login_time': login_time,
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'Unknown')
            })
            
            # Keep only last 10 logins
            if len(login_history[email]) > 10:
                login_history[email] = login_history[email][-10:]
            
            save_to_file(login_history, 'login_history.json')
            
            # Check if this is first login
            is_first_login = len(login_history[email]) == 1
            
            user_name = f"{users[email]['first_name']} {users[email]['last_name']}"
            
            # Email to admin about user login
            admin_subject = f"User Login Alert - {user_name}"
            admin_body = f"""
            <html>
            <body>
                <h2>🔔 User Login Notification</h2>
                <p><strong>User:</strong> {user_name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Role:</strong> {users[email]['role']}</p>
                <p><strong>Login Time:</strong> {login_time}</p>
                <p><strong>IP Address:</strong> {request.remote_addr}</p>
                <p><strong>First Login:</strong> {'Yes' if is_first_login else 'No'}</p>
                <hr>
                <p><em>This is an automated notification from Legezt Portal.</em></p>
            </body>
            </html>
            """
            
            # Send email to admin
            send_email(ADMIN_EMAIL, admin_subject, admin_body)
            
            # Send welcome email to user on first login
            if is_first_login:
                welcome_subject = "Welcome to Legezt Portal! 🎉"
                welcome_body = f"""
                <html>
                <body>
                    <h2>🎉 Welcome to Legezt Portal!</h2>
                    <p>Dear {user_name},</p>
                    <p>Welcome to Legezt Portal! We're excited to have you as part of our student community.</p>
                    <p>Here's what you can do with your account:</p>
                    <ul>
                        <li>📚 Access study materials from various colleges</li>
                        <li>🔍 Search and filter educational resources</li>
                        <li>📱 Use our mobile-friendly platform</li>
                        <li>👥 Connect with fellow students</li>
                    </ul>
                    <p>If you have any questions or need assistance, feel free to contact us.</p>
                    <hr>
                    <p><em>Best regards,<br>The Legezt Portal Team</em></p>
                </body>
                </html>
                """
                send_email(email, welcome_subject, welcome_body)
            
            # Check if admin needs verification
            if users[email]['role'] == 'pending_admin':
                return redirect(url_for('admin_verification'))
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # If user is already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        if email in users:
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        if role == 'admin':
            # Admin registration requires verification
            access_code = generate_access_code()
            
            users[email] = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': hashed_password,
                'role': 'pending_admin',
                'college': request.form.get('college', ''),
                'year': request.form.get('year', ''),
                'section': request.form.get('section', ''),
                'department': request.form.get('department', ''),
                'phone': request.form.get('phone', ''),
                'reason': request.form.get('reason', ''),
                'created_at': datetime.now().isoformat()
            }
            
            admin_verifications[email] = {
                'access_code': access_code,
                'created_at': datetime.now().isoformat(),
                'verified': False
            }
            
            # Send email to admin for verification
            email_body = f"""
            <h2>New Admin Registration Request</h2>
            <p>A new user has requested admin access:</p>
            <ul>
                <li><strong>Name:</strong> {first_name} {last_name}</li>
                <li><strong>Email:</strong> {email}</li>
                <li><strong>College:</strong> {request.form.get('college', 'N/A')}</li>
                <li><strong>Department:</strong> {request.form.get('department', 'N/A')}</li>
                <li><strong>Reason:</strong> {request.form.get('reason', 'N/A')}</li>
            </ul>
            <p><strong>Access Code:</strong> {access_code}</p>
            <p>Please verify this user and provide them with the access code.</p>
            """
            
            send_email(ADMIN_EMAIL, 'New Admin Registration Request', email_body)
            
            # Save data
            save_users(users)
            save_admin_verifications(admin_verifications)
            
            flash('Registration successful! Please wait for admin verification (24 hours).', 'success')
            return redirect(url_for('login'))
        else:
            # Student registration
            users[email] = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': hashed_password,
                'role': 'student',
                'created_at': datetime.now().isoformat()
            }
            
            save_users(users)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/admin_verification', methods=['GET', 'POST'])
def admin_verification():
    if 'user_id' not in session or users.get(session['user_id'], {}).get('role') != 'pending_admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        access_code = request.form['access_code']
        email = session['user_id']
        
        if email in admin_verifications and admin_verifications[email]['access_code'] == access_code:
            # Verify admin
            users[email]['role'] = 'admin'
            admin_verifications[email]['verified'] = True
            
            save_users(users)
            save_admin_verifications(admin_verifications)
            
            session['role'] = 'admin'
            flash('Admin verification successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid access code', 'error')
    
    return render_template('admin_verification.html')

@app.route('/resend_verification', methods=['POST'])
def resend_verification():
    """Resend admin verification email"""
    if 'user_id' not in session or users.get(session['user_id'], {}).get('role') != 'pending_admin':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    email = session['user_id']
    
    if email in admin_verifications and not admin_verifications[email]['verified']:
        # Generate new access code
        new_access_code = generate_access_code()
        admin_verifications[email]['access_code'] = new_access_code
        admin_verifications[email]['created_at'] = datetime.now().isoformat()
        
        # Save updated verification data
        save_admin_verifications(admin_verifications)
        
        # Send new verification email
        user_info = users[email]
        email_body = f"""
        <html>
        <body>
            <h2>🔄 Admin Verification Code Resent</h2>
            <p>Hello {user_info['first_name']} {user_info['last_name']},</p>
            <p>Your admin verification request has been resent. Here are your details:</p>
            
            <h3>📋 Request Details:</h3>
            <ul>
                <li><strong>Name:</strong> {user_info['first_name']} {user_info['last_name']}</li>
                <li><strong>Email:</strong> {email}</li>
                <li><strong>College:</strong> {user_info.get('college', 'N/A')}</li>
                <li><strong>Department:</strong> {user_info.get('department', 'N/A')}</li>
                <li><strong>Reason:</strong> {user_info.get('reason', 'N/A')}</li>
            </ul>
            
            <h3>🔐 New Access Code:</h3>
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 3px; color: #1f2937;">
                {new_access_code}
            </div>
            
            <p><strong>⚠️ Important:</strong> This code will expire in 24 hours for security reasons.</p>
            
            <p>Please use this code to complete your admin verification on the Legezt Portal.</p>
            
            <hr>
            <p><em>Best regards,<br>The Legezt Portal Team</em></p>
        </body>
        </html>
        """
        
        # Send email to admin for verification
        admin_email_body = f"""
        <html>
        <body>
            <h2>🔄 Admin Verification Request Resent</h2>
            <p>A user has requested to resend their admin verification code:</p>
            
            <h3>📋 User Details:</h3>
            <ul>
                <li><strong>Name:</strong> {user_info['first_name']} {user_info['last_name']}</li>
                <li><strong>Email:</strong> {email}</li>
                <li><strong>College:</strong> {user_info.get('college', 'N/A')}</li>
                <li><strong>Department:</strong> {user_info.get('department', 'N/A')}</li>
                <li><strong>Reason:</strong> {user_info.get('reason', 'N/A')}</li>
            </ul>
            
            <h3>🔐 New Access Code:</h3>
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 3px; color: #1f2937;">
                {new_access_code}
            </div>
            
            <p><strong>⏰ Request Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <p>Please verify this user and provide them with the new access code if approved.</p>
            
            <hr>
            <p><em>Best regards,<br>Legezt Portal System</em></p>
        </body>
        </html>
        """
        
        # Send emails
        send_email(email, 'Admin Verification Code Resent - Legezt Portal', email_body)
        send_email(ADMIN_EMAIL, 'Admin Verification Request Resent', admin_email_body)
        
        flash('Verification email has been resent! Please check your email for the new access code.', 'success')
    else:
        flash('Unable to resend verification email. Please contact support.', 'error')
    
    return redirect(url_for('admin_verification'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', files=files, branches=branches, subjects=subjects)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    # Check Google Drive connection status
    google_drive_connected = ensure_google_drive_connected()
    
    if request.method == 'POST':
        # Check if Google Drive is connected before allowing upload
        if not google_drive_connected:
            flash('Google Drive is not connected. Please connect first.', 'error')
            return render_template('upload.html', branches=branches, subjects=subjects, google_drive_connected=google_drive_connected)
        
        title = request.form['title']
        description = request.form['description']
        subject = request.form['subject']
        branch = request.form['branch']
        year = request.form['year']
        
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return render_template('upload.html', branches=branches, subjects=subjects, google_drive_connected=google_drive_connected)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return render_template('upload.html', branches=branches, subjects=subjects, google_drive_connected=google_drive_connected)
        
        # Validate file type
        allowed_extensions = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'zip', 'rar', 'jpg', 'jpeg', 'png', 'gif'}
        if not file.filename.lower().endswith(tuple('.' + ext for ext in allowed_extensions)):
            flash('Invalid file type. Allowed: PDF, DOC, DOCX, PPT, PPTX, TXT, ZIP, RAR, Images', 'error')
            return render_template('upload.html', branches=branches, subjects=subjects, google_drive_connected=google_drive_connected)
        
        try:
            # Read file data
            file_data = file.read()
            filename = f"{title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            
            # Upload to Google Drive using system account
            drive_result = upload_file_to_drive(file_data, filename)
            
            if not drive_result:
                flash('Failed to upload file to Google Drive. Please try again.', 'error')
                return render_template('upload.html', branches=branches, subjects=subjects, google_drive_connected=google_drive_connected)
            
            # Create shareable link
            shareable_link = create_shareable_link(drive_result['id'])
            if not shareable_link:
                flash('File uploaded but failed to create shareable link. Please try again.', 'error')
                return render_template('upload.html', branches=branches, subjects=subjects, google_drive_connected=google_drive_connected)
            
            # Create new file entry
            new_id = 1
            if files:
                new_id = max(f['id'] for f in files) + 1
            
            new_file = {
                'id': new_id,
                'title': title,
                'description': description,
                'subject': subject,
                'branch': branch,
                'year': year,
                'uploader': session['user_id'],
                'download_count': 0,
                'google_drive_link': shareable_link,
                'google_drive_id': drive_result['id'],
                'filename': filename,
                'original_filename': file.filename,
                'upload_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            files.append(new_file)
            save_files(files)  # Save to file
            flash('Material uploaded successfully to Google Drive!', 'success')
            return redirect(url_for('dashboard'))
                
        except Exception as e:
            print(f"✗ Upload error: {e}")
            flash('Error uploading material. Please try again.', 'error')
            return render_template('upload.html', branches=branches, subjects=subjects, google_drive_connected=google_drive_connected)
    
    return render_template('upload.html', branches=branches, subjects=subjects, google_drive_connected=google_drive_connected)

@app.route('/connect-google-drive')
def connect_google_drive():
    """Route to initiate Google Drive connection"""
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    auth_url = get_google_drive_auth_url()
    return redirect(auth_url)

@app.route('/disconnect-google-drive', methods=['POST'])
def disconnect_google_drive():
    """Disconnect from Google Drive"""
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('settings'))
    
    try:
        global ADMIN_GOOGLE_DRIVE_TOKEN
        
        # Clear the global token variable
        ADMIN_GOOGLE_DRIVE_TOKEN = None
        
        # Remove Google Drive tokens file
        token_file = 'google_drive_tokens.json'
        if os.path.exists(token_file):
            os.remove(token_file)
            print("✓ Google Drive tokens removed")
        
        flash('Google Drive has been disconnected successfully. New file uploads will not work until reconnected.', 'success')
        print("✓ Google Drive disconnected by admin")
        
    except Exception as e:
        flash(f'Error disconnecting Google Drive: {str(e)}', 'error')
        print(f"✗ Error disconnecting Google Drive: {e}")
    
    return redirect(url_for('settings'))

@app.route('/download/<int:file_id>')
def download(file_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    file = next((f for f in files if f['id'] == file_id), None)
    if file:
        # Increment download count
        file['download_count'] += 1
        save_files(files)  # Save to file
        return redirect(file['google_drive_link'])
    else:
        flash('File not found', 'error')
        return redirect(url_for('dashboard'))

@app.route('/file/edit/<int:file_id>', methods=['GET', 'POST'])
def edit_file(file_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    file = next((f for f in files if f['id'] == file_id), None)
    if not file:
        flash('File not found', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        subject = request.form['subject']
        branch = request.form['branch']
        year = request.form['year']
        
        # Update file information
        file['title'] = title
        file['description'] = description
        file['subject'] = subject
        file['branch'] = branch
        file['year'] = year
        
        save_files(files)
        flash('File updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_file.html', file=file, branches=branches, subjects=subjects)

@app.route('/file/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    file = next((f for f in files if f['id'] == file_id), None)
    if not file:
        flash('File not found', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Delete from Google Drive if we have the file ID
        if 'google_drive_id' in file:
            global ADMIN_GOOGLE_DRIVE_TOKEN
            if ensure_google_drive_connected():
                access_token = ADMIN_GOOGLE_DRIVE_TOKEN.get('access_token')
                if access_token:
                    delete_url = f'https://www.googleapis.com/drive/v3/files/{file["google_drive_id"]}'
                    headers = {
                        'Authorization': f'Bearer {access_token}'
                    }
                    response = requests.delete(delete_url, headers=headers)
                    if response.status_code == 204:
                        print(f"✓ File deleted from Google Drive: {file['filename']}")
                    else:
                        print(f"⚠ Failed to delete from Google Drive: {response.text}")
        
        # Remove from local storage
        files.remove(file)
        save_files(files)
        flash('File deleted successfully!', 'success')
        
    except Exception as e:
        print(f"✗ Error deleting file: {e}")
        flash('Error deleting file. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check Google Drive connection status
    google_drive_connected = ensure_google_drive_connected()
    
    return render_template('settings.html', google_drive_connected=google_drive_connected)

@app.route('/logout')
def logout():
    # Send logout notification if user was logged in
    if 'user_id' in session:
        user_email = session['user_id']
        if user_email in users:
            user_name = f"{users[user_email]['first_name']} {users[user_email]['last_name']}"
            logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Email to admin about user logout
            admin_subject = f"User Logout Alert - {user_name}"
            admin_body = f"""
            <html>
            <body>
                <h2>🚪 User Logout Notification</h2>
                <p><strong>User:</strong> {user_name}</p>
                <p><strong>Email:</strong> {user_email}</p>
                <p><strong>Role:</strong> {session.get('role', 'Unknown')}</p>
                <p><strong>Logout Time:</strong> {logout_time}</p>
                <p><strong>IP Address:</strong> {request.remote_addr}</p>
                <hr>
                <p><em>This is an automated notification from Legezt Portal.</em></p>
            </body>
            </html>
            """
            
            # Send email to admin
            send_email(ADMIN_EMAIL, admin_subject, admin_body)
    
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))

@app.route('/api/filter')
def filter_files():
    branch = request.args.get('branch', '')
    subject = request.args.get('subject', '')
    year = request.args.get('year', '')
    search = request.args.get('search', '').lower()
    
    filtered_files = files.copy()
    
    if branch:
        filtered_files = [f for f in filtered_files if f['branch'] == branch]
    if subject:
        filtered_files = [f for f in filtered_files if f['subject'] == subject]
    if year:
        filtered_files = [f for f in filtered_files if f['year'] == year]
    if search:
        filtered_files = [f for f in filtered_files if search in f['title'].lower() or search in f['description'].lower()]
    
    return jsonify(filtered_files)

@app.route('/api/stats')
def get_stats():
    """Get basic statistics for the dashboard"""
    total_files = len(files)
    total_downloads = sum(f['download_count'] for f in files)
    total_users = len(users)
    
    return jsonify({
        'total_files': total_files,
        'total_downloads': total_downloads,
        'total_users': total_users
    })

@app.route('/test-azure')
def test_azure():
    """Test Azure SQL connection"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': 'Azure SQL connected successfully',
                'version': version[0] if version else 'Unknown'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Query failed: {str(e)}'
            })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Azure SQL connection failed'
        })

@app.route('/login-stats')
def login_stats():
    """Admin view for login statistics"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Calculate statistics
    total_logins = sum(len(logins) for logins in login_history.values())
    unique_users = len(login_history)
    today_logins = 0
    today = datetime.now().strftime("%Y-%m-%d")
    
    for user_logins in login_history.values():
        for login in user_logins:
            if login['login_time'].startswith(today):
                today_logins += 1
    
    # Get recent logins
    recent_logins = []
    for email, logins in login_history.items():
        if email in users:
            user_name = f"{users[email]['first_name']} {users[email]['last_name']}"
            for login in logins[-3:]:  # Last 3 logins per user
                recent_logins.append({
                    'user_name': user_name,
                    'email': email,
                    'login_time': login['login_time'],
                    'ip_address': login['ip_address']
                })
    
    # Sort by login time (most recent first)
    recent_logins.sort(key=lambda x: x['login_time'], reverse=True)
    
    return jsonify({
        'total_logins': total_logins,
        'unique_users': unique_users,
        'today_logins': today_logins,
        'recent_logins': recent_logins[:20]  # Last 20 logins
    })

@app.route('/send-login-report')
def send_login_report():
    """Generate and send Excel report of login statistics"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Prepare data for Excel
        login_data = []
        user_stats = []
        
        # Collect all login records
        for email, logins in login_history.items():
            if email in users:
                user_name = f"{users[email]['first_name']} {users[email]['last_name']}"
                user_role = users[email]['role']
                
                # Add user statistics
                user_stats.append({
                    'User Name': user_name,
                    'Email': email,
                    'Role': user_role,
                    'Total Logins': len(logins),
                    'First Login': logins[0]['login_time'] if logins else 'N/A',
                    'Last Login': logins[-1]['login_time'] if logins else 'N/A'
                })
                
                # Add individual login records
                for login in logins:
                    login_data.append({
                        'User Name': user_name,
                        'Email': email,
                        'Role': user_role,
                        'Login Time': login['login_time'],
                        'IP Address': login['ip_address'],
                        'User Agent': login.get('user_agent', 'Unknown')
                    })
        
        # Create Excel file with multiple sheets
        with BytesIO() as output:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Sheet 1: User Statistics
                df_stats = pd.DataFrame(user_stats)
                df_stats.to_excel(writer, sheet_name='User Statistics', index=False)
                
                # Sheet 2: Detailed Login Records
                df_logins = pd.DataFrame(login_data)
                df_logins.to_excel(writer, sheet_name='Login Records', index=False)
                
                # Sheet 3: Summary Statistics
                summary_data = {
                    'Metric': [
                        'Total Users',
                        'Total Logins',
                        'Today\'s Logins',
                        'Active Users (Last 7 days)',
                        'Most Active User',
                        'Report Generated'
                    ],
                    'Value': [
                        len(login_history),
                        sum(len(logins) for logins in login_history.values()),
                        sum(1 for logins in login_history.values() 
                            for login in logins 
                            if login['login_time'].startswith(datetime.now().strftime("%Y-%m-%d"))),
                        len([email for email, logins in login_history.items() 
                             if any((datetime.now() - datetime.strptime(login['login_time'], "%Y-%m-%d %H:%M:%S")).days <= 7 
                                   for login in logins)]),
                        max(user_stats, key=lambda x: x['Total Logins'])['User Name'] if user_stats else 'N/A',
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ]
                }
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
            # Send email with Excel attachment
            from email.mime.base import MIMEBase
            from email import encoders
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = EMAIL_CONFIG['username']
            msg['To'] = ADMIN_EMAIL  # Send to admin email
            msg['Subject'] = f"Legezt Portal - Login Report ({datetime.now().strftime('%Y-%m-%d')})"
            
            # Email body
            body = f"""
            <html>
            <body>
                <h2>📊 Legezt Portal Login Report</h2>
                <p>Dear Admin,</p>
                <p>Please find attached the comprehensive login report for Legezt Portal.</p>
                
                <h3>📈 Quick Summary:</h3>
                <ul>
                    <li><strong>Total Users:</strong> {len(login_history)}</li>
                    <li><strong>Total Logins:</strong> {sum(len(logins) for logins in login_history.values())}</li>
                    <li><strong>Today's Logins:</strong> {sum(1 for logins in login_history.values() for login in logins if login['login_time'].startswith(datetime.now().strftime("%Y-%m-%d")))}</li>
                </ul>
                
                <h3>📋 Report Contents:</h3>
                <ol>
                    <li><strong>User Statistics:</strong> Summary of each user's login activity</li>
                    <li><strong>Login Records:</strong> Detailed login history with timestamps</li>
                    <li><strong>Summary:</strong> Overall platform statistics</li>
                </ol>
                
                <p><em>Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
                <hr>
                <p><em>Best regards,<br>Legezt Portal System</em></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Attach Excel file
            output.seek(0)
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(output.read())
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename=login_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            )
            msg.attach(attachment)
            
            # Send email
            server = smtplib.SMTP(EMAIL_CONFIG['server'], EMAIL_CONFIG['port'])
            if EMAIL_CONFIG['use_tls']:
                server.starttls()
            
            server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
            server.send_message(msg)
            server.quit()
            
            flash('Login report sent successfully to your email!', 'success')
            return redirect(url_for('dashboard'))
            
    except Exception as e:
        print(f"✗ Failed to generate login report: {e}")
        flash('Failed to generate login report. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/dev-info')
def dev_info():
    """Development information endpoint"""
    google_drive_status = {
        'configured': GOOGLE_DRIVE_CONFIG['client_id'] != 'your-google-drive-client-id',
        'folder_name': GOOGLE_DRIVE_CONFIG['folder_name'],
        'admin_email': GOOGLE_DRIVE_CONFIG['admin_email'],
        'connected': ensure_google_drive_connected(),
        'connection_type': 'Admin Account (Single Drive)',
        'persistent_storage': os.path.exists(TOKEN_FILE),
        'token_file': TOKEN_FILE
    }
    
    return jsonify({
        'app_name': 'Legezt Portal',
        'version': '1.0.0',
        'debug_mode': app.config['DEBUG'],
        'auto_reload': app.config['TEMPLATES_AUTO_RELOAD'],
        'templates_folder': app.template_folder,
        'static_folder': app.static_folder,
        'environment': os.getenv('FLASK_ENV', 'development'),
        'google_drive': google_drive_status,
        'test_endpoints': {
            'email': '/test-email',
            'google_drive': '/test-google-drive',
            'azure_sql': '/test-azure'
        }
    })

@app.route('/test-email')
def test_email():
    """Test email functionality"""
    try:
        test_subject = "Test Email from Legezt Portal"
        test_body = """
        <html>
        <body>
            <h2>🧪 Test Email</h2>
            <p>This is a test email to verify that the email system is working correctly.</p>
            <p><strong>Time:</strong> {}</p>
            <p><strong>From:</strong> {}</p>
            <p><strong>To:</strong> {}</p>
            <hr>
            <p><em>If you receive this email, the email system is working!</em></p>
        </body>
        </html>
        """.format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            EMAIL_CONFIG['username'],
            ADMIN_EMAIL
        )
        
        success = send_email(ADMIN_EMAIL, test_subject, test_body)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Test email sent successfully!',
                'from': EMAIL_CONFIG['username'],
                'to': ADMIN_EMAIL,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to send test email',
                'from': EMAIL_CONFIG['username'],
                'to': ADMIN_EMAIL
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Email test failed: {str(e)}',
            'from': EMAIL_CONFIG['username'],
            'to': ADMIN_EMAIL
        })

@app.route('/test-google-drive')
def test_google_drive():
    """Test Google Drive connection"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({
            'status': 'error',
            'message': 'Access denied. Admin privileges required.'
        })
    
    try:
        # Check if Google Drive is connected using persistent system
        if not ensure_google_drive_connected():
            return jsonify({
                'status': 'error',
                'message': 'Google Drive not connected. Please connect first.',
                'auth_url': url_for('google_drive_auth', _external=True)
            })
        
        # Test folder creation/access
        folder_id = get_or_create_legezt_folder()
        if folder_id:
            return jsonify({
                'status': 'success',
                'message': 'Google Drive connection working!',
                'folder_id': folder_id,
                'folder_name': GOOGLE_DRIVE_CONFIG['folder_name'],
                'connected': True
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to access or create Google Drive folder',
                'connected': True
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Google Drive test failed: {str(e)}',
            'connected': bool(session.get('google_drive_access_token'))
        })

def load_google_drive_tokens():
    """Load Google Drive tokens from persistent storage"""
    global ADMIN_GOOGLE_DRIVE_TOKEN
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                tokens = json.load(f)
                # Check if tokens are still valid
                if tokens.get('access_token') and tokens.get('refresh_token'):
                    # Check if access token is expired (Google tokens expire in 1 hour)
                    if 'expires_at' in tokens:
                        expires_at = datetime.fromisoformat(tokens['expires_at'])
                        if datetime.now() < expires_at:
                            ADMIN_GOOGLE_DRIVE_TOKEN = tokens
                            print("✓ Loaded valid Google Drive tokens from storage")
                            return True
                        else:
                            # Token expired, try to refresh
                            print("⚠ Access token expired, attempting refresh...")
                            return refresh_google_drive_token_persistent()
                    else:
                        # No expiry info, assume valid for now
                        ADMIN_GOOGLE_DRIVE_TOKEN = tokens
                        print("✓ Loaded Google Drive tokens from storage (no expiry info)")
                        return True
        return False
    except Exception as e:
        print(f"✗ Error loading tokens: {e}")
        return False

def save_google_drive_tokens(tokens):
    """Save Google Drive tokens to persistent storage"""
    try:
        # Add expiry time (1 hour from now)
        tokens['expires_at'] = (datetime.now() + timedelta(hours=1)).isoformat()
        
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
        print("✓ Saved Google Drive tokens to persistent storage")
        return True
    except Exception as e:
        print(f"✗ Error saving tokens: {e}")
        return False

def refresh_google_drive_token_persistent():
    """Refresh Google Drive access token using persistent storage"""
    global ADMIN_GOOGLE_DRIVE_TOKEN
    
    try:
        # Load current tokens from storage
        if not os.path.exists(TOKEN_FILE):
            return False
            
        with open(TOKEN_FILE, 'r') as f:
            current_tokens = json.load(f)
        
        refresh_token = current_tokens.get('refresh_token')
        if not refresh_token:
            return False
            
        token_url = 'https://oauth2.googleapis.com/token'
        data = {
            'client_id': GOOGLE_DRIVE_CONFIG['client_id'],
            'client_secret': GOOGLE_DRIVE_CONFIG['client_secret'],
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            new_tokens = response.json()
            # Keep the refresh token from storage
            new_tokens['refresh_token'] = refresh_token
            
            # Save updated tokens
            if save_google_drive_tokens(new_tokens):
                ADMIN_GOOGLE_DRIVE_TOKEN = new_tokens
                print("✓ Successfully refreshed Google Drive token")
                return True
            else:
                return False
        else:
            print(f"✗ Failed to refresh token: {response.text}")
            # If refresh fails, remove invalid tokens
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
            return False
    except Exception as e:
        print(f"✗ Error refreshing token: {e}")
        return False

def ensure_google_drive_connected():
    """Ensure Google Drive is connected, automatically refresh if needed"""
    global ADMIN_GOOGLE_DRIVE_TOKEN
    
    # First check if token file exists (this is the source of truth)
    if not os.path.exists(TOKEN_FILE):
        # Clear any stale tokens in memory
        ADMIN_GOOGLE_DRIVE_TOKEN = None
        return False
    
    # If we already have valid tokens in memory, check if they're still valid
    if ADMIN_GOOGLE_DRIVE_TOKEN and ADMIN_GOOGLE_DRIVE_TOKEN.get('access_token'):
        # Check if token is expired
        if 'expires_at' in ADMIN_GOOGLE_DRIVE_TOKEN:
            expires_at = datetime.fromisoformat(ADMIN_GOOGLE_DRIVE_TOKEN['expires_at'])
            if datetime.now() < expires_at:
                return True
            else:
                # Token expired, refresh it
                return refresh_google_drive_token_persistent()
        else:
            return True
    
    # Try to load tokens from storage
    if load_google_drive_tokens():
        return True
    
    # No valid tokens found
    return False

@app.route('/document-scanner', methods=['GET', 'POST'])
def document_scanner():
    """Advanced document scanner with camera capture and image editing"""
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check Google Drive connection
    google_drive_connected = ensure_google_drive_connected()
    
    if request.method == 'POST':
        # Handle the final PDF upload
        if 'final_pdf' in request.files:
            file = request.files['final_pdf']
            title = request.form.get('title', 'Scanned Document')
            description = request.form.get('description', 'Document scanned using advanced scanner')
            subject = request.form.get('subject', '')
            branch = request.form.get('branch', '')
            year = request.form.get('year', '')
            
            if file and file.filename:
                # Read file data
                file_data = file.read()
                filename = f"{title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                # Upload to Google Drive
                drive_result = upload_file_to_drive(file_data, filename)
                if drive_result:
                    # Create shareable link
                    shareable_link = create_shareable_link(drive_result['id'])
                    
                    # Save file metadata
                    new_file = {
                        'id': len(files) + 1,
                        'title': title,
                        'description': description,
                        'filename': filename,
                        'original_filename': file.filename,
                        'subject': subject,
                        'branch': branch,
                        'year': year,
                        'upload_date': datetime.now().isoformat(),
                        'downloads': 0,
                        'uploaded_by': session['user_id'],
                        'google_drive_id': drive_result['id'],
                        'google_drive_link': shareable_link,
                        'file_type': 'pdf',
                        'file_size': len(file_data)
                    }
                    
                    files.append(new_file)
                    save_files(files)
                    
                    flash('Document scanned and uploaded successfully!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Failed to upload scanned document to Google Drive.', 'error')
            else:
                flash('No PDF file provided.', 'error')
    
    # Load subjects for dropdown
    subjects = load_subjects()
    
    return render_template('document_scanner.html', 
                         google_drive_connected=google_drive_connected,
                         subjects=subjects)

@app.route('/save-scanned-images', methods=['POST'])
def save_scanned_images():
    """Save scanned images temporarily for editing"""
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Create temp directory for scanned images
        temp_dir = 'temp_scanned_images'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Generate unique session ID for this scanning session
        session_id = f"scan_{session['user_id']}_{int(datetime.now().timestamp())}"
        session['scan_session_id'] = session_id
        
        # Save uploaded images
        uploaded_files = request.files.getlist('images')
        saved_images = []
        
        for i, file in enumerate(uploaded_files):
            if file and file.filename:
                # Generate unique filename
                filename = f"{session_id}_page_{i+1}.jpg"
                filepath = os.path.join(temp_dir, filename)
                
                # Save image
                file.save(filepath)
                saved_images.append({
                    'filename': filename,
                    'filepath': filepath,
                    'page_number': i + 1
                })
        
        session['scanned_images'] = saved_images
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'image_count': len(saved_images),
            'images': saved_images
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process-edited-images', methods=['POST'])
def process_edited_images():
    """Process edited images and convert to PDF"""
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get edited image data from request
        edited_images_data = request.json.get('edited_images', [])
        
        if not edited_images_data:
            return jsonify({'error': 'No edited images provided'}), 400
        
        # Create temp directory for processed images
        temp_dir = 'temp_processed_images'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        session_id = session.get('scan_session_id', f"scan_{session['user_id']}_{int(datetime.now().timestamp())}")
        
        # Process each edited image
        processed_images = []
        
        for i, image_data in enumerate(edited_images_data):
            # Decode base64 image data
            import base64
            image_data = image_data.split(',')[1]  # Remove data:image/jpeg;base64, prefix
            image_bytes = base64.b64decode(image_data)
            
            # Save processed image
            filename = f"{session_id}_processed_page_{i+1}.jpg"
            filepath = os.path.join(temp_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            processed_images.append(filepath)
        
        # Convert images to PDF using PIL and reportlab
        from PIL import Image
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, A4
        from io import BytesIO
        
        # Create PDF
        pdf_filename = f"{session_id}_scanned_document.pdf"
        pdf_filepath = os.path.join(temp_dir, pdf_filename)
        
        # Get the first image to determine page size
        if processed_images:
            with Image.open(processed_images[0]) as img:
                img_width, img_height = img.size
                # Convert to points (1 inch = 72 points)
                page_width = img_width * 72 / 96  # Assuming 96 DPI
                page_height = img_height * 72 / 96
        else:
            page_width, page_height = A4
        
        # Create PDF with custom page size
        c = canvas.Canvas(pdf_filepath, pagesize=(page_width, page_height))
        
        for image_path in processed_images:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as temporary JPEG
                temp_jpeg = BytesIO()
                img.save(temp_jpeg, format='JPEG', quality=95)
                temp_jpeg.seek(0)
                
                # Add image to PDF
                c.drawImage(temp_jpeg, 0, 0, width=page_width, height=page_height)
                c.showPage()
        
        c.save()
        
        # Read the generated PDF
        with open(pdf_filepath, 'rb') as f:
            pdf_data = f.read()
        
        # Clean up temporary files
        for image_path in processed_images:
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Return PDF data as base64
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
        
        return jsonify({
            'success': True,
            'pdf_data': pdf_base64,
            'pdf_filename': pdf_filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Test Azure SQL connection
    print("Testing Azure SQL Database connection...")
    connection = get_db_connection()
    if connection:
        print("✓ Azure SQL Database is ready!")
        connection.close()
    else:
        print("⚠ Using mock data mode - Azure SQL connection failed")
        print("💡 To fix Azure SQL connection:")
        print("   1. Install Microsoft ODBC Driver 18 for SQL Server")
        print("   2. Download from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
        print("   3. Or use the mock data mode which works perfectly")
    
    # Initialize Google Drive connection
    print("\n🔗 Initializing Google Drive connection...")
    if ensure_google_drive_connected():
        print("✓ Google Drive is connected and ready!")
    else:
        print("⚠ Google Drive not connected - admin will need to connect on first upload")
        print("💡 Admin can connect by going to /upload and clicking 'Connect Google Drive'")
    
    print("\n🚀 Starting Flask with Auto-Reload...")
    print("📝 Any changes to Python files or templates will auto-restart the server!")
    print("🌐 Access your app at: http://localhost:5000")
    print("🔧 Development info at: http://localhost:5000/dev-info")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True) 