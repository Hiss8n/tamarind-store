CREATE TABLE IF NOT EXISTS cart_items (
	item_name VARCHAR(120) NOT NULL PRIMARY KEY,
	item_count INT NOT NULL CHECK (item_count > 0),
	price DECIMAL(10, 2) NOT NULL CHECK (price > 0)
);