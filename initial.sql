CREATE TABLE IF NOT EXISTS recipes (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255) NOT NULL UNIQUE,
	category VARCHAR(100) NOT NULL,
	description TEXT,
	prep_time INT, --minutes
	instructions TEXT,
	image_url VARCHAR(255)
);


--CREATE TABLE IF NOT EXISTS ingredients (
--	id SERIAL PRIMARY KEY,
--	recipe_id INT REFERENCES recipes(id),
--	name VARCHAR(255),
--	quantity VARCHAR(50)
--);


CREATE TABLE IF NOT EXISTS comments (
	id SERIAL PRIMARY KEY,
	recipe_id INT REFERENCES recipes(id),
	content TEXT,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
