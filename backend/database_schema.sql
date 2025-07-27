-- SQL Schema showing the Foreign Key relationship between users and roles tables

-- Roles table (Primary table)
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Insert the two required roles
INSERT INTO roles (name) VALUES ('admin'), ('customer');

-- Users table with Foreign Key to roles
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INTEGER NOT NULL REFERENCES roles(id),  -- FOREIGN KEY
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role_id ON users(role_id);  -- FK index
CREATE INDEX idx_roles_name ON roles(name);

-- Example data insertion with FK relationship:

-- Insert sample users with proper role_id foreign keys
INSERT INTO users (username, email, password_hash, role_id, is_verified, address_line1, city, state, postal_code, country) VALUES 
('admin_user', 'admin@sweetshop.com', '$2b$12$hashedpassword1', 1, true, '123 Admin St', 'New York', 'NY', '10001', 'USA'),
('john_customer', 'john@example.com', '$2b$12$hashedpassword2', 2, true, '456 Customer Ave', 'Los Angeles', 'CA', '90210', 'USA'),
('jane_customer', 'jane@example.com', '$2b$12$hashedpassword3', 2, false, '789 Sweet Blvd', 'Chicago', 'IL', '60601', 'USA');

-- Example queries using the FK relationship:

-- Get all users with their role names and verification status
SELECT u.username, u.email, r.name as role_name, u.is_verified, u.created_at
FROM users u 
JOIN roles r ON u.role_id = r.id
ORDER BY u.created_at DESC;

-- Get all admin users with full details
SELECT u.username, u.email, u.address_line1, u.city, u.state, u.country
FROM users u 
JOIN roles r ON u.role_id = r.id 
WHERE r.name = 'admin';

-- Get all verified customer users
SELECT u.username, u.email, u.is_verified, u.created_at
FROM users u 
JOIN roles r ON u.role_id = r.id 
WHERE r.name = 'customer' AND u.is_verified = true;

-- Count users by role
SELECT r.name as role_name, COUNT(u.id) as user_count
FROM roles r
LEFT JOIN users u ON r.id = u.role_id
GROUP BY r.id, r.name
ORDER BY user_count DESC;

-- Get unverified customers for email verification
SELECT u.username, u.email, u.created_at
FROM users u 
JOIN roles r ON u.role_id = r.id 
WHERE r.name = 'customer' AND u.is_verified = false
ORDER BY u.created_at ASC;
