-- Legezt Portal Database Schema
-- Create database
CREATE DATABASE IF NOT EXISTS legezt_portal;
USE legezt_portal;

-- Users table (for both students and admins)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role ENUM('student', 'admin', 'pending_admin') DEFAULT 'student',
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    profile_picture VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    reset_password_token VARCHAR(255),
    reset_password_expires TIMESTAMP NULL
);

-- Admin verification table
CREATE TABLE admin_verifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    access_code VARCHAR(10) NOT NULL,
    college VARCHAR(255) NOT NULL,
    class_year VARCHAR(50) NOT NULL,
    section VARCHAR(10) NOT NULL,
    department VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    reason_for_admin TEXT,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    admin_notes TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Branches table
CREATE TABLE branches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subjects table
CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    branch_id INT NOT NULL,
    year INT NOT NULL,
    semester INT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE
);

-- Files table (for storing PDF and other materials)
CREATE TABLE files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    google_drive_id VARCHAR(255) NOT NULL,
    google_drive_link VARCHAR(500) NOT NULL,
    subject_id INT NOT NULL,
    uploaded_by INT NOT NULL,
    download_count INT DEFAULT 0,
    is_public BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    tags JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Download logs table
CREATE TABLE download_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id INT NOT NULL,
    user_id INT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Email logs table
CREATE TABLE email_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipient_email VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    email_type ENUM('verification', 'reset_password', 'admin_verification', 'welcome') NOT NULL,
    status ENUM('sent', 'failed', 'pending') DEFAULT 'pending',
    error_message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User sessions table (for security)
CREATE TABLE user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Rate limiting table
CREATE TABLE rate_limits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL,
    endpoint VARCHAR(100) NOT NULL,
    request_count INT DEFAULT 1,
    first_request TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_request TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ip_endpoint (ip_address, endpoint)
);

-- Insert default branches
INSERT INTO branches (name, code, description) VALUES
('Computer Science Engineering', 'CSE', 'Computer Science and Engineering'),
('Information Technology', 'IT', 'Information Technology'),
('Electronics and Communication', 'ECE', 'Electronics and Communication Engineering'),
('Mechanical Engineering', 'MECH', 'Mechanical Engineering'),
('Civil Engineering', 'CIVIL', 'Civil Engineering'),
('Electrical Engineering', 'EEE', 'Electrical and Electronics Engineering');

-- Insert default subjects for CSE
INSERT INTO subjects (name, code, branch_id, year, semester, description) VALUES
('Programming Fundamentals', 'CSE101', 1, 1, 1, 'Introduction to programming concepts'),
('Data Structures', 'CSE201', 1, 2, 1, 'Fundamental data structures and algorithms'),
('Database Management Systems', 'CSE301', 1, 3, 1, 'Database design and SQL'),
('Computer Networks', 'CSE401', 1, 4, 1, 'Network protocols and architecture'),
('Software Engineering', 'CSE402', 1, 4, 2, 'Software development methodologies');

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_files_subject ON files(subject_id);
CREATE INDEX idx_files_uploaded_by ON files(uploaded_by);
CREATE INDEX idx_download_logs_file ON download_logs(file_id);
CREATE INDEX idx_download_logs_user ON download_logs(user_id);
CREATE INDEX idx_email_logs_recipient ON email_logs(recipient_email);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token); 