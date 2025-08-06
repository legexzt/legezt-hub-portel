# Legezt Portal - Student Resource Management System

A comprehensive Flask-based web application for managing and sharing educational resources, study materials, and college notes.

## 🚀 Features

### Core Features
- **User Authentication**: Secure login/register system with email verification
- **Admin Panel**: Complete admin dashboard with user management
- **File Management**: Upload, organize, and share study materials
- **College Structure**: Hierarchical organization (College → Year → Semester → Branch → Subject)
- **Google Drive Integration**: Automatic file storage and sharing
- **Email Notifications**: Login/logout notifications and admin reports
- **Document Scanner**: Built-in document scanning and processing
- **Responsive Design**: Modern UI that works on all devices

### Technical Features
- **Flask Framework**: Python web framework
- **Azure SQL Database**: Cloud database with JSON fallback
- **Google Drive API**: File storage and sharing
- **SMTP Email**: Namecheap Private Email integration
- **Tailwind CSS**: Modern styling framework
- **Auto-reload**: Development server with hot reload
- **Session Management**: Secure user sessions
- **Excel Reports**: Admin login statistics and reports

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Google Drive API credentials
- Namecheap Private Email account
- Azure SQL Database (optional)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/legezt-portal.git
cd legezt-portal
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables
Create a `.env` file in the root directory:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DB_HOST=localhost
DB_USER=iamlegezt
DB_PASSWORD=mehonjibraan_09
DB_NAME=legezt_portal

# Email Configuration (SMTP - Namecheap Private Email)
MAIL_SERVER=smtp.privateemail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=mohdjibraan@legezthub.me
MAIL_PASSWORD=iamlegezt09

# Google Drive API Configuration
GOOGLE_DRIVE_CLIENT_ID=your-client-id
GOOGLE_DRIVE_CLIENT_SECRET=your-client-secret
GOOGLE_DRIVE_REDIRECT_URI=http://localhost:5000/auth/google/callback
GOOGLE_DRIVE_API_KEY=your-api-key

# Admin Email (for admin verification)
ADMIN_EMAIL=mdjibjibran@gmail.com

# JWT Secret (For authentication)
JWT_SECRET=any_long_random_string

# Azure SQL Database (optional)
DB_SERVER=legexzt-server.database.windows.net
DB_NAME=legezt-app
DB_PORT=1433
```

### 6. Run the Application
```bash
python app_auto_reload.py
```

The application will be available at: **http://localhost:5000**

## 📁 Project Structure

```
legezt-portal/
├── app_auto_reload.py          # Main Flask application
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation
├── database_schema.sql         # Database schema
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── splash.html            # Splash screen
│   ├── home.html              # Home page
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── dashboard.html         # User dashboard
│   ├── college_notes.html     # College materials
│   ├── settings.html          # User settings
│   ├── upload.html            # File upload
│   └── about.html             # About page
├── static/                    # Static files
│   ├── css/                   # Stylesheets
│   │   ├── input.css          # Tailwind input
│   │   ├── output.css         # Compiled CSS
│   │   └── style.css          # Custom styles
│   ├── js/                    # JavaScript files
│   ├── images/                # Images and logos
│   ├── videos/                # Video files
│   └── favicon_io/            # Favicon files
└── venv/                      # Virtual environment
```

## 🔧 Configuration

### Google Drive Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Drive API
4. Create OAuth 2.0 credentials
5. Add credentials to `.env` file

### Email Setup
1. Configure Namecheap Private Email SMTP settings
2. Update `.env` file with email credentials
3. Test email functionality

### Database Setup
- **Development**: Uses JSON files for data storage
- **Production**: Configure Azure SQL Database connection

## 🚀 Deployment

### Local Development
```bash
python app_auto_reload.py
```

### Production Deployment
1. Set `FLASK_ENV=production` in `.env`
2. Configure production database
3. Set up proper SSL certificates
4. Use a production WSGI server (Gunicorn, uWSGI)

## 📊 Features Overview

### User Features
- ✅ User registration and login
- ✅ Email verification
- ✅ Profile management
- ✅ File upload and download
- ✅ College materials browsing
- ✅ Document scanning
- ✅ Settings management

### Admin Features
- ✅ User management
- ✅ File approval system
- ✅ Login statistics
- ✅ Excel report generation
- ✅ Email notifications
- ✅ Google Drive integration

### Technical Features
- ✅ Responsive design
- ✅ Auto-reload development server
- ✅ Session management
- ✅ Error handling
- ✅ Logging system
- ✅ Security features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Email: mdjibjibran@gmail.com
- GitHub Issues: [Create an issue](https://github.com/yourusername/legezt-portal/issues)

## 🔄 Version History

- **v1.0.0** - Initial release with core features
- **v1.1.0** - Added Google Drive integration
- **v1.2.0** - Added email notifications and admin reports
- **v1.3.0** - Added document scanner feature
- **v1.4.0** - Improved UI/UX and responsive design

---

**Made with ❤️ by Legezt Team** 