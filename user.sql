USE hbnb_dev_db;

CREATE TABLE user (
	id INT AUTO_INCREMENT PRIMARY KEY,
	username VARCHAR(255) DEFAULT 'default_username',
	email VARCHAR(255) NOT NULL UNIQUE,
	password VARCHAR(255) DEFAULT 'default_password',
	password_hash VARCHAR(255);
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

