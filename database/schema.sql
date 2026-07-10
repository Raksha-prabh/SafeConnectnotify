CREATE DATABASE safeconnect;

USE safeconnect;

CREATE TABLE users(
id INT PRIMARY KEY AUTO_INCREMENT,
name VARCHAR(100),
email VARCHAR(100),
password VARCHAR(255)
);

CREATE TABLE profile_analysis(
id INT PRIMARY KEY AUTO_INCREMENT,
username VARCHAR(100),
risk_score INT,
risk_level VARCHAR(50),
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fake_accounts(
id INT PRIMARY KEY AUTO_INCREMENT,
username VARCHAR(100),
probability FLOAT,
result VARCHAR(100)
);

CREATE TABLE friend_checks(
id INT PRIMARY KEY AUTO_INCREMENT,
username VARCHAR(100),
trust_score INT,
recommendation VARCHAR(100)
);