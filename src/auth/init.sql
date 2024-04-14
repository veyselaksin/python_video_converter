CREATE USER 'auth_user'@'localhost' IDENTIFIED BY 'auth_password';

CREATE DATABASE auth_db;

GRANT ALL PRIVILEGES ON auth_db.* TO 'auth_user'@'localhost';

USE auth_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

INSERT INTO users (username, password) VALUES ('admin', 'password');
