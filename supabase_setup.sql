-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table to store user information
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    registration_time TIMESTAMP WITH TIME ZONE NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Create file_uploads table to store metadata of uploaded files
CREATE TABLE file_uploads (
    file_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    upload_time TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT valid_file_name CHECK (file_name ~* '^[A-Za-z0-9][A-Za-z0-9._-]*\.[A-Za-z0-9]+$')
);

-- Create data_preprocessing_logs table to track preprocessing activities
CREATE TABLE data_preprocessing_logs (
    preprocess_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID NOT NULL,
    user_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('completed', 'failed', 'pending')),
    preprocess_time TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (file_id) REFERENCES file_uploads(file_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Create datasets table to store preprocessed dataset metadata
CREATE TABLE datasets (
    dataset_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID NOT NULL,
    user_id UUID NOT NULL,
    dataset_name VARCHAR(255) NOT NULL,
    storage_path VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (file_id) REFERENCES file_uploads(file_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT valid_dataset_name CHECK (dataset_name ~* '^[A-Za-z0-9][A-Za-z0-9._-]*_preprocessed\.csv$')
);

-- Create indexes to optimize query performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_file_uploads_user_id ON file_uploads(user_id);
CREATE INDEX idx_file_uploads_file_id ON file_uploads(file_id);
CREATE INDEX idx_data_preprocessing_logs_file_id ON data_preprocessing_logs(file_id);
CREATE INDEX idx_data_preprocessing_logs_user_id ON data_preprocessing_logs(user_id);
CREATE INDEX idx_datasets_file_id ON datasets(file_id);
CREATE INDEX idx_datasets_user_id ON datasets(user_id);





CREATE TABLE IF NOT EXISTS users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password TEXT NOT NULL,
  registration_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login_timestamp TIMESTAMP
);
