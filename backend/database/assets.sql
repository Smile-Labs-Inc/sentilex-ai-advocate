-- Create the database if it doesn't already exist
CREATE DATABASE IF NOT EXISTS sentilex_db;
USE sentilex_db;

-- Create the lawyers table
CREATE TABLE IF NOT EXISTS lawyers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialties VARCHAR(255) NOT NULL,
    experience_years INT NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    district VARCHAR(50) NOT NULL,
    availability ENUM('Available', 'In Consultation', 'Offline') DEFAULT 'Available',
    rating DECIMAL(2,1) DEFAULT 0.0,
    reviews_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Use the database
USE sentilex_db;

-- Drop existing table if it exists
DROP TABLE IF EXISTS lawyers;

-- Create the lawyers table with corrected ENUM (no spaces)
CREATE TABLE lawyers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialties VARCHAR(255) NOT NULL,
    experience_years INT NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    district VARCHAR(50) NOT NULL,
    availability ENUM('Available', 'InConsultation', 'Offline') DEFAULT 'Available',
    rating DECIMAL(2,1) DEFAULT 0.0,
    reviews_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert all lawyer records with updated availability values
INSERT INTO lawyers 
(name, specialties, experience_years, email, phone, district, availability, rating, reviews_count) 
VALUES 
('Aris Thorne', 'Criminal Law', 12, 'aris.thorne@legal.com', '555-0101', 'Downtown', 'Available', 4.8, 120),
('Elena Vance', 'Family Law', 8, 'elena.vance@law.com', '555-0102', 'Northside', 'InConsultation', 4.5, 85),
('Julian Marsh', 'Corporate Law', 15, 'j.marsh@corp.com', '555-0103', 'Financial District', 'Available', 4.9, 210),
('Sarah Chen', 'Intellectual Property', 6, 'schen@techlaw.com', '555-0104', 'West End', 'Offline', 4.2, 45),
('Marcus Reed', 'Real Estate', 20, 'mreed@realty.com', '555-0105', 'East Side', 'Available', 4.7, 150),
('Fiona Gallagher', 'Employment Law', 10, 'fgallagher@labor.com', '555-0106', 'South Park', 'InConsultation', 4.6, 92),
('Liam O\'Connor', 'Tax Law', 9, 'liam.oc@finance.com', '555-0107', 'Central', 'Available', 4.4, 60),
('Maya Patel', 'Environmental Law', 7, 'mpatel@green.com', '555-0108', 'Green Valley', 'Available', 4.3, 38),
('Victor Hugo', 'Civil Rights', 25, 'vhugo@justice.com', '555-0109', 'Old Town', 'Offline', 5.0, 300),
('Diana Prince', 'International Law', 14, 'dprince@global.com', '555-0110', 'Embassy Row', 'Available', 4.8, 115);

-- Verify the data was inserted correctly
SELECT * FROM lawyers;

-- Show the table structure
DESCRIBE lawyers;